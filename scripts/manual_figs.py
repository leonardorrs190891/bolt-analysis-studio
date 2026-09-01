# -*- coding: utf-8 -*-
"""Gera as 5 figuras-chave do Manual BAS V2 a partir do STORE REAL.

Por que este script existe (gate da F6, plano-mestre §6.2/§6.3): *toda* afirmação
numérica do Manual tem de sair do store/ledger, "nada de número solto". Se as
figuras E os números vierem do mesmo script versionado, o gate se cumpre por
construção — o Manual cita `figs/numbers.json`, que é gerado aqui, e não valores
digitados à mão que envelhecem em silêncio (a mesma doença que a regra do
fingerprint, §4.43, pega no roadmap).

    python scripts/manual_figs.py            # SVGs (claro + escuro) + numbers.json
    python scripts/manual_figs.py --dump     # só imprime os números, nada escrito
    python scripts/manual_figs.py --check    # verifica que os SVGs estão em dia

Saída: docs/MANUAL_BAS_V2/figs/{fig1..fig5}.svg (+ `-dark.svg`) e numbers.json.

As 5 figuras (§6.2 do plano):
  1. anatomia da curva — estágios, joelho, piso
  2. decomposição por mecanismo (empilhada)
  3. painel de validação — MAE × resíduo máximo dos 203 casos, com o tripé
  4. tornado de sensibilidade (§4.42), com os congelados S≈0 em cinza
  5. mapa formas × fontes — a tese "formas transferem, constantes não", medida

CONVENÇÕES DE GRÁFICO (não são gosto, são regra verificada). A paleta é a
categórica validada: rodei o validador de CVD nos três conjuntos usados aqui —
3 slots em *all-pairs* para o dispersão (pior par CVD ΔE 9,2 claro / 9,4 escuro)
e 6 slots em *adjacentes* para a pilha (9,1 claro / 8,4 escuro), nos DOIS modos.
Os slots claros aqua/amarelo/magenta ficam abaixo de 3:1 contra a superfície
clara, então a regra de alívio se aplica e as figuras trazem **rótulo direto**
(além da tabela equivalente no próprio Manual). Marcas finas: linha 2 px,
marcador ≥8 px com anel de 2 px na cor da superfície, malha em fio de cabelo
SÓLIDO (nunca tracejada), preenchimento de área a ~10 %, vão de 2 px separando
faixas empilhadas. Um eixo por gráfico — nunca dois eixos y.

TEMA: as duas variantes são GERADAS, não uma inversão automática — os passos
escuros são os da própria paleta para superfície escura, validados como conjunto.
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import matplotlib
matplotlib.use("Agg")                       # sem display; roda em CI/headless
import matplotlib.pyplot as plt             # noqa: E402
import numpy as np                          # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

OUT_DIR = ROOT / "docs" / "MANUAL_BAS_V2" / "figs"
STORE = ROOT / "Models" / "CALIBRATION_AND_VALIDATION" / "validation_store.json"
ADOPTED = ROOT / "New_Theory" / "adopted_configs.json"

META_ALVO = 0.10                            # o tripé: MAE < 0,10 E res.máx < 0,10

# --------------------------------------------------------------------------
# Tema — os dois modos vêm da paleta validada, cada um com seus passos
# --------------------------------------------------------------------------
TEMAS = {
    "light": dict(
        surface="#fcfcfb", ink="#0b0b0b", ink2="#52514e", muted="#898781",
        grid="#e1e0d9", axis="#c3c2b7",
        cat=["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300",
             "#4a3aa7", "#e34948"],
        good="#0ca30c", warn="#fab219", crit="#d03b3b",
    ),
    "dark": dict(
        surface="#1a1a19", ink="#ffffff", ink2="#c3c2b7", muted="#898781",
        grid="#2c2c2a", axis="#383835",
        cat=["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181", "#008300",
             "#9085e9", "#e66767"],
        good="#0ca30c", warn="#fab219", crit="#d03b3b",
    ),
}

FAMILIA_ROTULO = {"transverse": "transversal", "axial": "axial", "creep": "creep"}

# Agrupamento das constantes dos cfg adotados em FORMAS (famílias de mecanismo).
# Serve à figura 5: cada linha é uma forma do engine, cada coluna uma fonte de
# dado; a célula acende quando o cfg adotado daquela fonte mexe em algum campo
# da forma. Densidade da LINHA = a forma reaparece em muitos rigs (transfere);
# a variação dos VALORES (que a figura não mostra, e o Manual tabela) é a outra
# metade da tese.
FORMAS = [
    ("Assentamento (embedding)",
     {"emb_um", "emb_depth", "N_emb", "emb_load_frac", "emb_amp_exp",
      "rho_ref_emb", "p_ref_emb", "emb", "k_emb_renew"}),
    ("Creep (log)",
     {"C_creep", "creep_mode", "creep_t_c", "creep_alpha_sat",
      "creep_conform_exp", "t_0"}),
    ("Desgaste (Archard/fretting)",
     {"k_wear_spec", "K_archard", "k_wear_scale_tr", "k_wear_running",
      "N_wear_run", "k_gall"}),
    ("Afrouxamento rotacional",
     {"tr_loose_gain", "k_ratchet", "loose_rate_mode", "s_crit_loose"}),
    ("Auto-travamento (piso)", {"loose_arrest_floor"}),
    ("Dano de superfície D",
     {"c_D", "k_dmg_mu", "k_dmg_wear", "c_D_per_lube", "c_D_dry", "c_D_oil",
      "W_ref", "dmg_dwell_exp", "f_ref_dmg"}),
    ("Modos de flexão / membro", {"c_bend", "delta_free", "GA_member"}),
    ("Atrito (µ)", {"mu", "mu_thread", "mu_bearing", "free_spin"}),
    ("Conformação por pressão", {"W_conf_ref"}),
    ("Incubação de escorregamento", {"slip_onset_W", "slip_regime_mode"}),
    ("Rigidez do membro (k_j)", {"kj_mode"}),
]


# --------------------------------------------------------------------------
# Carga de dados
# --------------------------------------------------------------------------
def carrega_store() -> Dict[str, dict]:
    return json.loads(STORE.read_text(encoding="utf-8"))


def carrega_registry():
    from bolt_analysis_studio.validation.case_registry import all_records
    return {r.case_id: r for r in all_records()}


def censo(store: Dict[str, dict], reg) -> dict:
    """Os números que o Manual cita. Um lugar só, lido do store.

    DUAS armadilhas de contagem, as duas medidas em 2026-07-28 e tratadas aqui
    em vez de deixadas para quem lê:

    1. **Id fora do registry.** O store canônico já ganhou registro de teste
       (`ensaio_teste_m12`, 203 -> 204) por uma escrita indevida. Um censo que
       soma `len(store)` herda o lixo. Aqui os intrusos são SEPARADOS e
       contados à parte — se `n_fora_do_registry` não for 0, há escrita indevida
       no store versionado (guarda em `tests/test_validation_store.py`).
    2. **202 vs 203.** O registry inclui `exemplo_m12_sintetico`, o caso de
       exemplo do próprio app (fonte `USER`), legítimo e mantido por decisão do
       S2. Ele conta no store mas NÃO no censo certificado da literatura. Por
       isso publicamos os dois números com nome: `n_comparaveis` (tudo que tem
       MAE) e `n_comparaveis_lit` (só dado de artigo) — foi a ambiguidade entre
       eles que fez a mesma campanha citar 202, 203 e 204 em dias diferentes.
    """
    conhecidos = set(reg)
    intrusos = sorted(set(store) - conhecidos)
    store = {k: v for k, v in store.items() if k in conhecidos}
    comp = {k: v for k, v in store.items() if v.get("mae") is not None}
    comp_lit = {k: v for k, v in comp.items()
                if getattr(reg.get(k), "source", "") != "USER"}
    tripe_lit = [k for k, v in comp_lit.items()
                 if v["mae"] < META_ALVO
                 and (v.get("maxerr") is None or v["maxerr"] < META_ALVO)]
    maes = np.array([v["mae"] for v in comp.values()])
    mxs = np.array([(v.get("maxerr") if v.get("maxerr") is not None else 0.0)
                    for v in comp.values()])
    no_tripe = [k for k, v in comp.items()
                if v["mae"] < META_ALVO
                and (v.get("maxerr") is None or v["maxerr"] < META_ALVO)]
    so_mae = [k for k, v in comp.items()
              if v["mae"] >= META_ALVO
              and (v.get("maxerr") is not None and v["maxerr"] < META_ALVO)]
    so_max = [k for k, v in comp.items()
              if v["mae"] < META_ALVO
              and (v.get("maxerr") is not None and v["maxerr"] >= META_ALVO)]
    ambos = [k for k, v in comp.items()
             if v["mae"] >= META_ALVO
             and (v.get("maxerr") is not None and v["maxerr"] >= META_ALVO)]

    # por fonte: quantas fecham o tripé
    por_fonte: Dict[str, List[int]] = {}
    for k in comp:
        r = reg.get(k)
        src = getattr(r, "source", "(fora do registry)")
        d = por_fonte.setdefault(src, [0, 0])
        d[0] += 1
        if k in no_tripe:
            d[1] += 1
    fontes_100 = sorted(s for s, (n, ok) in por_fonte.items() if n == ok)

    fps = sorted({str(v.get("engine_fingerprint")) for v in store.values()})
    l7 = [v["l7_check"] for v in store.values() if v.get("l7_check")]
    l7_com_valor = [x for x in l7 if x.get("implied_J_per_mm3")]
    l7_fora = [x for x in l7_com_valor if not x.get("in_bound")]

    return dict(
        n_registros=len(store),
        n_fora_do_registry=len(intrusos), ids_fora_do_registry=intrusos,
        n_comparaveis=len(comp),
        n_comparaveis_lit=len(comp_lit),
        n_tripe_lit=len(tripe_lit),
        pct_tripe_lit=round(100.0 * len(tripe_lit) / max(len(comp_lit), 1), 1),
        n_tripe=len(no_tripe),
        pct_tripe=round(100.0 * len(no_tripe) / max(len(comp), 1), 1),
        n_fora=len(comp) - len(no_tripe),
        n_so_mae=len(so_mae), n_so_maxerr=len(so_max), n_ambos=len(ambos),
        mae_mediana=round(float(np.median(maes)), 4),
        mae_media=round(float(maes.mean()), 4),
        maxerr_mediana=round(float(np.median(mxs)), 4),
        n_erros=sum(1 for v in store.values()
                    if not v.get("ok", False) or v.get("error")),
        fingerprints=fps,
        n_fontes=len(por_fonte),
        n_fontes_100=len(fontes_100),
        fontes_100=fontes_100,
        por_fonte={s: dict(n=n, tripe=ok) for s, (n, ok) in
                   sorted(por_fonte.items())},
        l7_n_com_valor=len(l7_com_valor), l7_n_fora_da_banda=len(l7_fora),
        l7_banda=(l7_com_valor[0]["bound"] if l7_com_valor else None),
    )


# --------------------------------------------------------------------------
# Infra de gráfico
# --------------------------------------------------------------------------
def _fig(t: dict, w=7.4, h=4.3) -> Tuple[plt.Figure, plt.Axes]:
    plt.rcParams.update({
        "svg.hashsalt": "bas-v2-manual",     # SVG determinístico => diff limpo
        "font.family": "DejaVu Sans",
        "font.size": 8.5, "axes.titlesize": 10, "axes.labelsize": 9,
        "xtick.labelsize": 8, "ytick.labelsize": 8,
        "figure.dpi": 110,
    })
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor(t["surface"])
    ax.set_facecolor(t["surface"])
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    for lado in ("left", "bottom"):
        ax.spines[lado].set_color(t["axis"])
        ax.spines[lado].set_linewidth(0.8)
    ax.tick_params(colors=t["muted"], length=3, width=0.8)
    ax.grid(True, which="major", color=t["grid"], linewidth=0.8,
            linestyle="-", zorder=0)          # fio de cabelo SÓLIDO
    ax.set_axisbelow(True)
    return fig, ax


def _titulo(ax, t: dict, titulo: str, sub: str = "") -> None:
    """`pad=28` NÃO é enfeite: com o pad de 14 que estava aqui, o título e o
    subtítulo se sobrepunham em TODAS as cinco figuras (visto na inspeção PNG de
    2026-07-28). O título fica acima de 28 pt do topo dos eixos; o subtítulo
    ocupa 7..16 pt. Validador de paleta checa cor, não colisão de rótulo — por
    isso o passo de renderizar-e-olhar existe."""
    ax.set_title(titulo, color=t["ink"], loc="left", pad=28 if sub else 8,
                 fontweight="bold")
    if sub:
        ax.annotate(sub, xy=(0, 1.0), xycoords="axes fraction",
                    xytext=(0, 7), textcoords="offset points",
                    color=t["ink2"], fontsize=8.5, va="bottom")


def _legenda(ax, t: dict, **kw) -> None:
    lg = ax.legend(frameon=False, labelcolor=t["ink2"], fontsize=8, **kw)
    for txt in lg.get_texts():                # texto NUNCA veste a cor da série
        txt.set_color(t["ink2"])


# destino/formato de inspeção (--png <dir>): serve ao passo "renderize e OLHE"
# — validador de paleta checa cor, não colisão de rótulo nem estouro de caixa.
_INSPECAO: Optional[Path] = None


def _salva(fig, nome: str, modo: str) -> Path:
    if _INSPECAO is not None:
        _INSPECAO.mkdir(parents=True, exist_ok=True)
        p = _INSPECAO / (f"{nome}.png" if modo == "light"
                         else f"{nome}-dark.png")
        fig.savefig(p, format="png", bbox_inches="tight", dpi=110,
                    facecolor=fig.get_facecolor())
        plt.close(fig)
        return p
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    p = OUT_DIR / (f"{nome}.svg" if modo == "light" else f"{nome}-dark.svg")
    # LF EXPLICITO, e nao e' preciosismo: o .gitattributes deste repo declara
    # `*.svg text eol=lf`, mas o matplotlib escreve em modo TEXTO e no Windows
    # isso vira CRLF. Medido em 2026-07-28: index em LF, copia de trabalho em
    # CRLF (`git ls-files --eol` -> i/lf w/crlf) => o arquivo no disco NAO era o
    # que um checkout produz, e o gate (C), que compara bytes, acusaria os 10
    # SVGs como "DEFASADO" em qualquer clone novo — falha espuria que ensinaria
    # a ignorar o gate. `metadata={"Date": None}` tira a data de criacao (sem
    # isso nem duas rodadas na mesma maquina batem); o `newline` faz o resto.
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        fig.savefig(fh, format="svg", bbox_inches="tight",
                    facecolor=fig.get_facecolor(), metadata={"Date": None})
    plt.close(fig)
    return p


def _barra_arred(ax, x0, y, larg, alt, cor, r_pt=0.045):
    """Barra horizontal com a PONTA DE DADO arredondada (4 px) e a base
    quadrada. `FancyBboxPatch` arredonda os quatro cantos, então cobrimos a
    base com um retângulo — é o jeito de obter a especificação de marca sem
    desenhar contorno (contorno adiciona tinta que não é dado)."""
    if larg <= 0:
        return
    r = min(r_pt, abs(larg) / 2)
    ax.add_patch(FancyBboxPatch((x0, y - alt / 2), larg, alt,
                                boxstyle=f"round,pad=0,rounding_size={r}",
                                linewidth=0, facecolor=cor, zorder=3,
                                mutation_aspect=1))
    ax.add_patch(Rectangle((x0, y - alt / 2), min(r, larg), alt, linewidth=0,
                           facecolor=cor, zorder=3))


# --------------------------------------------------------------------------
# FIG 1 — anatomia da curva
# --------------------------------------------------------------------------
def escolhe_caso_anatomia(store, reg) -> Tuple[str, str]:
    """Escolhe o caso da figura 1 por REGRA DETERMINÍSTICA e declarada — a
    figura não pode ser escolha a dedo, senão ela ilustra o melhor caso e não o
    fenômeno.

    A regra é uma CASCATA, e o nível que de fato pegou é devolvido e vai para o
    `numbers.json`. A primeira tentativa (só «transversal + no tripé + perda >
    0,30 + MAE mediano») pegou `karlsen2022_M30_HV_run6p2`, que é uma queda quase
    reta com 8 pontos: cumpria a regra e NÃO mostrava nem patamar nem joelho.
    Uma figura chamada «anatomia» tem de ter a anatomia, então a regra passou a
    exigir o patamar explicitamente — em vez de eu trocar o caso na mão.
    """
    base = []
    for k, v in store.items():
        r = reg.get(k)
        if r is None or getattr(r, "family", "") != "transverse":
            continue
        if v.get("mae") is None or not v.get("metric_data"):
            continue
        if v["mae"] >= META_ALVO or (v.get("maxerr") or 0) >= META_ALVO:
            continue
        md, mx = v["metric_data"], v["metric_x"]
        perda = md[0] - min(md)
        if perda < 0.30:
            continue
        # fração da perda já consumida nos primeiros 10 % dos ciclos: patamar
        # de Estágio I = valor BAIXO (o assentamento sozinho não derruba a curva)
        lim = mx[0] + 0.10 * (mx[-1] - mx[0])
        dentro = [y for x, y in zip(mx, md) if x <= lim] or [md[0]]
        cedo = (md[0] - min(dentro)) / max(perda, 1e-9)
        # o PISO só vale como elemento da figura se a curva de fato o encostar;
        # um `loose_arrest_floor` de 0,08 sob uma curva que para em 0,62 desenha
        # uma reta vermelha longe de tudo e não ensina nada
        piso = ((v.get("config_used") or {}).get("overrides")
                or {}).get("loose_arrest_floor")
        piso_util = (isinstance(piso, (int, float)) and 0 < float(piso) < 1
                     and abs(float(md[-1]) - float(piso)) < 0.10)
        base.append((v["mae"], k, len(mx), cedo, piso_util))

    niveis = (
        ("patamar<25%, >=12 pontos e piso ENCOSTADO pela curva",
         lambda z: z[3] < 0.25 and z[2] >= 12 and z[4]),
        ("patamar<25% e >=10 pontos", lambda z: z[3] < 0.25 and z[2] >= 10),
        ("perda>0,30 e no tripe", lambda z: True),
    )
    for nome, ok in niveis:
        cand = sorted(z for z in base if ok(z))
        if cand:
            # o critério final é MENOR MAE, e isso É uma escolha de caso bem
            # ajustado — declarada aqui e DECLARADA NA LEGENDA da figura, com
            # ponteiro para a figura 3, que mostra a distribuição inteira
            # (inclusive as curvas que não fecham a meta). Uma figura que ensina
            # anatomia precisa de um exemplar onde a anatomia apareça; a
            # honestidade vem de dizer isso e de publicar o resto ao lado.
            return cand[0][1], nome
    raise SystemExit("nenhum caso atende a regra da figura 1")


def _joelho(x: np.ndarray, y: np.ndarray) -> Tuple[float, float]:
    """N onde metade da perda total já ocorreu (definição do ledger para N50)."""
    perda = y[0] - y
    total = perda[-1] if perda[-1] > 1e-9 else perda.max()
    if total <= 1e-9:
        return float(x[len(x) // 2]), float(y[len(y) // 2])
    i = int(np.argmax(perda >= 0.5 * total))
    return float(x[i]), float(y[i])


def fig1(store, reg, modo: str, cid: str) -> dict:
    t, v = TEMAS[modo], store[cid]
    x = np.asarray(v["metric_x"], float)
    yd = np.asarray(v["metric_data"], float)
    yp = np.asarray(v["metric_pred"], float)
    piso = ((v.get("config_used") or {}).get("overrides")
            or {}).get("loose_arrest_floor")

    fig, ax = _fig(t)
    # estágios (0-10 / 10-70 / 70-100 % dos ciclos) — as janelas do report
    n0, n1 = float(x.min()), float(x.max())
    for a, b, rot in ((0.0, 0.10, "I"), (0.10, 0.70, "II"), (0.70, 1.0, "III")):
        xa, xb = n0 + a * (n1 - n0), n0 + b * (n1 - n0)
        if rot == "II":
            ax.axvspan(xa, xb, color=t["grid"], alpha=0.55, zorder=0, lw=0)
        # y em COORDENADA DE DADO (ylim vai a 1.09): em fração de eixo, 1.045
        # caía na faixa do título e os rótulos I e II ficavam invisíveis
        ax.annotate(f"estágio {rot}" if rot == "I" else rot,
                    xy=((xa + xb) / 2, 1.045), ha="center",
                    color=t["muted"], fontsize=8)

    ax.plot(x, yd, marker="o", markersize=4.5, linewidth=2, color=t["cat"][0],
            markeredgecolor=t["surface"], markeredgewidth=1.2,
            solid_capstyle="round", label="dado do artigo", zorder=4)
    ax.plot(x, yp, linewidth=2, color=t["cat"][1], solid_capstyle="round",
            label="modelo (alinhado, = o que o MAE mede)", zorder=5)

    xj, yj = _joelho(x, yd)
    ax.plot([xj], [yj], marker="o", markersize=9, color=t["cat"][0],
            markeredgecolor=t["surface"], markeredgewidth=2, zorder=6)
    # ACIMA-À-DIREITA do joelho: numa curva monótona decrescente essa é a única
    # vizinhança garantidamente vazia. Com o deslocamento anterior (10, −16) o
    # rótulo saía riscado pela própria curva.
    ax.annotate(f"joelho · N={xj:,.0f}".replace(",", " "), xy=(xj, yj),
                xytext=(12, 15), textcoords="offset points",
                color=t["ink"], fontsize=8.5, fontweight="bold")

    if isinstance(piso, (int, float)) and 0 < float(piso) < 1:
        ax.axhline(float(piso), color=t["crit"], linewidth=1.4, zorder=2)
        # à ESQUERDA, logo acima da linha: no fim da curva o rótulo era cortado
        # pelas duas séries, que chegam justamente no piso
        ax.annotate(f"piso de auto-travamento  {float(piso):.2f}·F₀",
                    xy=(n0, float(piso)), xytext=(4, 5),
                    textcoords="offset points", ha="left",
                    color=t["ink2"], fontsize=8)

    ax.set_xlabel("ciclos N")
    ax.set_ylabel("F/F₀  (pré-carga retida)")
    ax.set_ylim(0, 1.09)
    _titulo(ax, t, "1 · Anatomia de uma curva de auto-afrouxamento",
            f"{cid} — MAE {v['mae']:.4f} · resíduo máx {v['maxerr']:.4f}")
    _legenda(ax, t, loc="lower left")
    p = _salva(fig, "fig1_anatomia", modo)

    return dict(
        arquivo=p.name, caso=cid, mae=round(v["mae"], 4),
        maxerr=round(v["maxerr"], 4), joelho_N=round(xj), joelho_r=round(yj, 3),
        piso=(round(float(piso), 3) if isinstance(piso, (int, float)) else None),
        r_inicial=round(float(yd[0]), 3), r_final=round(float(yd[-1]), 3),
        perda_total=round(float(yd[0] - yd[-1]), 3),
        variaveis=("eixo x = número de ciclos N; eixo y = F/F₀, a fração da "
                   "pré-carga inicial ainda retida. Azul = dado digitalizado do "
                   "artigo; laranja = modelo, já dividido pelo divisor de "
                   "alinhamento (é a curva que o MAE mede). A faixa cinza é o "
                   "Estágio II; I/II/III são as janelas 0-10 %, 10-70 % e "
                   "70-100 % dos ciclos."),
        como_ler=("Procure três coisas: o patamar inicial (Estágio I, "
                  "assentamento), o joelho onde a queda acelera (marcado no "
                  "ponto em que metade da perda total já ocorreu) e o piso "
                  "onde a curva estabiliza — no modelo esse piso é a comporta "
                  "de auto-travamento, não um ajuste. A distância vertical "
                  "entre as duas curvas em cada N é o resíduo."),
        ressalva=("Esta curva foi escolhida por regra declarada e determinística "
                  "para EXIBIR a anatomia (patamar + joelho + piso encostado), e "
                  "o critério final é o menor MAE entre as que passam — ou seja, "
                  "é um caso bem ajustado, não um caso médio. A distribuição "
                  "completa, inclusive as curvas que não cumprem a meta, está na "
                  "figura 3; a mediana do conjunto é o número a usar quando se "
                  "quer «quão bom é o modelo»."),
    )


# --------------------------------------------------------------------------
# FIG 2 — decomposição por mecanismo
# --------------------------------------------------------------------------
def fig2(store, reg, modo: str, cid: str) -> dict:
    t, v = TEMAS[modo], store[cid]
    x = np.asarray(v["cycles"], float)
    dec = v.get("decomp") or {}
    rot = {"embedding": "assentamento", "creep": "creep", "wear": "desgaste",
           "rotational_loosening": "afrouxamento rotacional",
           "thread_fretting": "fretting de rosca", "fatigue": "fadiga"}
    ordem = ["embedding", "creep", "wear", "rotational_loosening",
             "thread_fretting", "fatigue"]

    series, rotulos, cores, finais = [], [], [], {}
    outros = np.zeros_like(x)
    islot = 0
    for m in ordem:
        y = np.asarray(dec.get(m) or [0.0] * len(x), float)
        finais[rot[m]] = round(float(y[-1]), 4)
        if float(y[-1]) < 0.005:              # <0,5 % da perda: dobra em "outros"
            outros = outros + y
            continue
        series.append(y)
        rotulos.append(rot[m])
        cores.append(t["cat"][islot])
        islot += 1
    if outros[-1] > 1e-9:
        series.append(outros)
        rotulos.append("outros (<0,5 % cada)")
        cores.append(t["muted"])

    fig, ax = _fig(t)
    faixas = ax.stackplot(x, *series, labels=rotulos, colors=cores,
                          edgecolor=t["surface"], linewidth=2.0, zorder=3)
    #      ^ o `edgecolor` na cor da superfície É o vão de 2 px entre faixas
    total = np.sum(series, axis=0)
    ax.plot(x, total, linewidth=2, color=t["ink"], solid_capstyle="round",
            zorder=5, label="perda total = 1 − F/F₀")

    # rótulo direto na faixa mais grossa (regra de alívio p/ os slots claros)
    espessuras = [float(s[-1]) for s in series]
    imax = int(np.argmax(espessuras))
    base = float(np.sum([s[-1] for s in series[:imax]]))
    ax.annotate(f"{rotulos[imax]}  {100*espessuras[imax]/max(total[-1],1e-9):.0f} %",
                xy=(x[-1], base + espessuras[imax] / 2),
                xytext=(-8, 0), textcoords="offset points", ha="right",
                va="center", color=t["ink"], fontsize=8.5,
                fontweight="bold")

    ax.set_xlabel("ciclos N")
    ax.set_ylabel("perda de pré-carga acumulada  (fração de F₀)")
    ax.set_xlim(float(x.min()), float(x.max()))
    ax.set_ylim(0, max(float(total.max()) * 1.18, 1e-3))
    _titulo(ax, t, "2 · De onde vem a perda: decomposição por mecanismo",
            f"{cid} — as parcelas somam exatamente 1 − F/F₀")
    _legenda(ax, t, loc="upper left", ncol=2)
    p = _salva(fig, "fig2_decomposicao", modo)

    soma = float(total[-1])
    return dict(
        arquivo=p.name, caso=cid, perda_total_final=round(soma, 4),
        parcelas_finais=finais,
        dominante=(rotulos[imax], round(100 * espessuras[imax] / max(soma, 1e-9), 1)),
        variaveis=("eixo x = ciclos N; eixo y = perda de pré-carga acumulada, "
                   "em fração de F₀. Cada faixa é um dos mecanismos de perda "
                   "que rodam em paralelo no engine; a linha preta é a soma, "
                   "que fecha exatamente com 1 − F/F₀ da figura 1 — não é um "
                   "ajuste da soma, é contabilidade fechada."),
        como_ler=("A ESPESSURA de cada faixa em um dado N é quanto aquele "
                  "mecanismo já tirou de pré-carga até ali; a INCLINAÇÃO é a "
                  "taxa instantânea. Mecanismos que aparecem cedo e saturam "
                  "(assentamento) empilham na base; os que crescem com o "
                  "escorregamento (desgaste, afrouxamento rotacional) engrossam "
                  "depois do joelho. Mecanismo com menos de 0,5 % da perda "
                  "final foi dobrado em «outros» para não poluir a legenda."),
    )


# --------------------------------------------------------------------------
# FIG 3 — painel de validação
# --------------------------------------------------------------------------
def fig3(store, reg, modo: str, cs: dict) -> dict:
    t = TEMAS[modo]
    # dispersão = pairlist ALL-PAIRS => teto de 3 slots categóricos validados;
    # são exatamente as 3 famílias do registry, então ninguém sobra.
    fam_cor = {"transverse": t["cat"][0], "axial": t["cat"][1],
               "creep": t["cat"][2]}
    pts: Dict[str, List[Tuple[float, float]]] = {k: [] for k in fam_cor}
    fora_de_escala = []
    for k, v in store.items():
        if v.get("mae") is None:
            continue
        r = reg.get(k)
        fam = getattr(r, "family", None)
        if fam not in fam_cor:
            continue
        # o painel é de validação contra LITERATURA: o caso de exemplo do
        # próprio app (fonte USER) fica fora, senão o título diz 203 e a
        # legenda da meta diz 202, que foi exatamente a ambiguidade que fez a
        # campanha citar três números diferentes para o mesmo censo
        if getattr(r, "source", "") == "USER":
            continue
        mae, mx = float(v["mae"]), float(v.get("maxerr") or 0.0)
        if mx > 0.62:                    # cauda longuíssima: anotada, não cortada
            fora_de_escala.append((k, mae, mx))
            mx = 0.62
        pts[fam].append((mae, mx))

    fig, ax = _fig(t, w=7.4, h=4.6)
    # a caixa do tripé: a meta é uma REGIÃO, não uma linha
    ax.add_patch(Rectangle((0, 0), META_ALVO, META_ALVO, facecolor=t["cat"][0],
                           alpha=0.10, linewidth=0, zorder=1))
    ax.axvline(META_ALVO, color=t["axis"], linewidth=0.8, zorder=2)
    ax.axhline(META_ALVO, color=t["axis"], linewidth=0.8, zorder=2)
    # a legenda da meta vai para o vazio à DIREITA, com linha-guia até a caixa:
    # posta dentro da caixa (como estava) ela cobria justamente o aglomerado de
    # pontos que ela descreve
    ax.annotate(f"tripé: MAE < {META_ALVO:.2f}  E  res.máx < {META_ALVO:.2f}\n"
                f"{cs['n_tripe_lit']} de {cs['n_comparaveis_lit']} curvas de "
                f"artigo ({cs['pct_tripe_lit']:.0f} %)",
                xy=(META_ALVO, 0.055), xytext=(0.20, 0.055),
                color=t["ink"], fontsize=8.5, va="center", fontweight="bold",
                zorder=6,
                arrowprops=dict(arrowstyle="-", color=t["axis"], lw=0.8))

    for fam, cor in fam_cor.items():
        if not pts[fam]:
            continue
        a = np.array(pts[fam])
        ax.plot(a[:, 0], a[:, 1], linestyle="none", marker="o", markersize=8,
                color=cor, markeredgecolor=t["surface"], markeredgewidth=2,
                alpha=0.9, label=f"{FAMILIA_ROTULO[fam]} (n={len(a)})", zorder=4)

    ax.plot([0, 0.7], [0, 0.7], color=t["muted"], linewidth=0.8, zorder=2)
    # rótulo DENTRO do intervalo visível: em (0,55; 0,55) ele era recortado pelo
    # xlim de 0,42 e a diagonal ficava sem explicação nenhuma na figura
    ax.annotate("res.máx = MAE — nada existe abaixo\n(o pico é ≥ a média, por "
                "definição)", xy=(0.315, 0.315), xytext=(6, -4),
                textcoords="offset points", ha="left", va="top",
                color=t["muted"], fontsize=7.5, rotation=0)

    extra = ""
    if fora_de_escala:
        extra = (f" · {len(fora_de_escala)} caso(s) além de 0,62 "
                 f"(máx {max(m for _, _, m in fora_de_escala):.2f}) fixados na "
                 f"borda superior")

    ax.set_xlabel("MAE (erro médio absoluto em F/F₀)")
    ax.set_ylabel("resíduo máximo")
    ax.set_xlim(0, 0.42)
    ax.set_ylim(0, 0.65)
    _titulo(ax, t, f"3 · Onde estão as {cs['n_comparaveis_lit']} curvas de "
                   f"artigo, e o que falta fechar",
            f"store {cs['fingerprints'][0]} · mediana MAE {cs['mae_mediana']:.4f}"
            f" · {cs['n_fora']} fora do tripé{extra}")
    _legenda(ax, t, loc="upper right")     # a legenda da meta ocupa o rodape
    p = _salva(fig, "fig3_painel", modo)

    return dict(
        arquivo=p.name, n=cs["n_comparaveis"], n_tripe=cs["n_tripe"],
        n_so_mae=cs["n_so_mae"], n_so_maxerr=cs["n_so_maxerr"],
        n_ambos=cs["n_ambos"], fora_de_escala=[k for k, _, _ in fora_de_escala],
        escopo="curvas de artigo (o caso de exemplo do app, fonte USER, fica fora)",
        variaveis=("cada ponto é UMA curva de validação: eixo x = MAE, eixo y = "
                   "resíduo máximo, os dois em unidades de F/F₀. Cor = família "
                   "de carregamento (transversal, axial, creep). O retângulo "
                   "azul é a meta — o «tripé» — e a diagonal cinza é o limite "
                   "geométrico res.máx = MAE."),
        como_ler=("Só o que cai DENTRO do retângulo cumpriu a meta. A leitura "
                  f"que muda a estratégia: dos {cs['n_fora']} casos fora, "
                  f"{cs['n_so_maxerr']} violam SÓ o resíduo máximo e "
                  f"{cs['n_so_mae']} violam só o MAE — ou seja, o gargalo é o "
                  "PICO, não a média. Esforço medido em MAE médio não move esta "
                  "figura; encurtar o pior ponto de cada curva move."),
    )


# --------------------------------------------------------------------------
# FIG 4 — tornado de sensibilidade
# --------------------------------------------------------------------------
def fig4(modo: str) -> dict:
    from bolt_analysis_studio.calibration import knowledge_base as kb
    t = TEMAS[modo]
    sens, congelados = kb.sensitivity(), kb.frozen_params()
    itens = sorted(((k, float(d.get("max") or 0.0), float(d.get("mean") or 0.0))
                    for k, d in sens.items()), key=lambda z: z[1])
    for k in congelados:                       # os S≈0 entram como zero explícito
        if k not in sens:
            itens.insert(0, (k, 0.0, 0.0))

    fig, ax = _fig(t, w=7.4, h=max(4.2, 0.30 * len(itens) + 1.4))
    for i, (k, mx, _mean) in enumerate(itens):
        # DUAS coisas diferentes, e a versão anterior desta figura rotulava as
        # duas de "congelado (§4.42c)" — o que é falso para a segunda:
        #  · congelado NO REGISTRO  = `parameter_registry.FROZEN_S_ZERO`; o
        #    otimizador nunca o recebe como candidato (decisão gravada);
        #  · S≈0 MEDIDO             = o tornado deu zero, mas o parâmetro segue
        #    ofertável. Chamar isso de "congelado" numa figura de manual sobre
        #    honestidade seria exatamente o erro que o manual denuncia.
        travado, zero_medido = k in congelados, mx <= 0.0
        cor = t["muted"] if (travado or zero_medido) else t["cat"][0]
        _barra_arred(ax, 0, i, mx, 0.55, cor, r_pt=0.0035)
        if travado:
            ax.annotate("congelado no registro (S≈0, §4.42c)", xy=(0.0016, i),
                        va="center", color=t["ink2"], fontsize=7.5, zorder=4)
        elif zero_medido:
            ax.annotate("S≈0 medido (não congelado)", xy=(0.0016, i),
                        va="center", color=t["muted"], fontsize=7.5, zorder=4)
        else:
            ax.annotate(f"{mx:.3f}", xy=(mx, i), xytext=(5, 0),
                        textcoords="offset points", va="center",
                        color=t["ink2"], fontsize=7.5)
    ax.set_yticks(range(len(itens)))
    ax.set_yticklabels([k for k, _, _ in itens], color=t["ink2"], fontsize=8)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("|ΔF/F₀| máximo produzido por variar o parâmetro sozinho (OAT)")
    ax.set_xlim(0, max(mx for _, mx, _ in itens) * 1.22)
    _titulo(ax, t, "4 · Quais constantes o modelo realmente sente",
            f"{len(sens)} parâmetros varridos um-a-um · "
            f"{len(congelados)} congelados por S≈0")
    p = _salva(fig, "fig4_tornado", modo)

    return dict(
        arquivo=p.name, n_parametros=len(sens), n_congelados=len(congelados),
        congelados=sorted(congelados),
        top5=[(k, round(mx, 4)) for k, mx, _ in reversed(itens[-5:])],
        variaveis=("uma barra por parâmetro; comprimento = maior variação de "
                   "F/F₀ que o parâmetro produz quando é o ÚNICO a mudar "
                   "(varredura um-a-um, OAT). Barras cinza são os parâmetros "
                   "com sensibilidade nula, congelados no registro para que o "
                   "otimizador nunca os ofereça."),
        como_ler=("Leia de cima para baixo: as primeiras barras são as "
                  "constantes que merecem procedência cuidadosa, porque o "
                  "resultado depende delas. As barras cinza são a contagem "
                  "honesta de graus de liberdade — parâmetro que não move "
                  "nada não é um grau de liberdade escondido, e está "
                  "explicitamente travado no código."),
    )


# --------------------------------------------------------------------------
# FIG 5 — mapa formas × fontes
# --------------------------------------------------------------------------
def fig5(reg, modo: str) -> dict:
    t = TEMAS[modo]
    srcs = json.loads(ADOPTED.read_text(encoding="utf-8"))["sources"]
    fontes_reg = sorted({getattr(r, "source", "") for r in reg.values()
                         if getattr(r, "source", "")})

    # cada chave de cfg adotado pertence à fonte cujo prefixo ela carrega
    def fonte_de(chave: str) -> Optional[str]:
        cands = [f for f in fontes_reg if chave.upper().startswith(f.upper())]
        return max(cands, key=len) if cands else None

    campos_por_fonte: Dict[str, set] = {}
    for chave, blk in srcs.items():
        f = fonte_de(chave)
        if f is None:
            continue
        alvo = campos_por_fonte.setdefault(f, set())
        alvo |= set((blk.get("cfg") or {}).keys())
        for pc in (blk.get("per_case") or {}).values():
            if isinstance(pc, dict):
                alvo |= set(pc.keys())

    cols = [f for f in fontes_reg if f in campos_por_fonte]
    # linhas ORDENADAS por densidade (a mais universal no topo). A leitura da
    # figura é por linha — deixá-las na ordem em que eu escrevi FORMAS jogava a
    # linha mais forte (assentamento, 20/26) no rodapé, onde ninguém começa.
    formas = sorted(FORMAS,
                    key=lambda fc: -sum(1 for f in cols
                                        if fc[1] & campos_por_fonte[f]))
    M = np.zeros((len(formas), len(cols)), dtype=bool)
    for i, (_, campos) in enumerate(formas):
        for j, f in enumerate(cols):
            M[i, j] = bool(campos & campos_por_fonte[f])
    M = M[::-1]                       # eixo y do matplotlib cresce p/ cima
    formas = formas[::-1]

    fig, ax = _fig(t, w=max(7.6, 0.30 * len(cols) + 4.2),
                   h=0.34 * len(formas) + 2.4)
    ax.grid(False)
    for i in range(len(formas)):
        for j in range(len(cols)):
            if M[i, j]:
                ax.add_patch(Rectangle((j + 0.12, i + 0.12), 0.76, 0.76,
                                       facecolor=t["cat"][0], linewidth=0,
                                       zorder=3))
            else:
                ax.add_patch(Rectangle((j + 0.12, i + 0.12), 0.76, 0.76,
                                       facecolor=t["grid"], linewidth=0,
                                       zorder=2))
    for i, (nome, _) in enumerate(formas):
        n = int(M[i].sum())
        ax.annotate(f"{n}/{len(cols)}", xy=(len(cols) + 0.35, i + 0.5),
                    va="center", color=t["ink"], fontsize=8,
                    fontweight="bold")
    ax.set_xlim(0, len(cols) + 2.1)
    ax.set_ylim(0, len(formas))
    ax.set_yticks([i + 0.5 for i in range(len(formas))])
    ax.set_yticklabels([n for n, _ in formas], color=t["ink2"], fontsize=8.5)
    ax.set_xticks([j + 0.5 for j in range(len(cols))])
    ax.set_xticklabels(cols, rotation=90, color=t["muted"], fontsize=7)
    ax.tick_params(length=0)
    for lado in ("left", "bottom"):
        ax.spines[lado].set_visible(False)
    ax.annotate("fontes ativas", xy=(len(cols) + 0.35, len(formas)),
                xytext=(0, 6), textcoords="offset points",
                color=t["muted"], fontsize=7.5, fontweight="bold")
    _titulo(ax, t, "5 · Formas transferem entre bancadas; constantes não",
            f"{len(formas)} formas do engine × {len(cols)} fontes com config "
            f"adotada — célula acesa = a forma está ativa naquela fonte")
    p = _salva(fig, "fig5_formas_fontes", modo)

    linhas = {nome: int(M[i].sum()) for i, (nome, _) in enumerate(formas)}
    return dict(
        arquivo=p.name, n_formas=len(formas), n_fontes=len(cols),
        fontes=cols, ativacoes_por_forma=linhas,
        forma_mais_universal=max(linhas.items(), key=lambda z: z[1]),
        variaveis=("linhas = formas (famílias de mecanismo) do engine; colunas "
                   "= fontes de dado com configuração adotada; célula acesa = a "
                   "configuração daquela fonte mexe em pelo menos uma constante "
                   "daquela forma. O número à direita conta em quantas fontes a "
                   "forma aparece."),
        como_ler=("Leia por LINHA, não por célula: uma linha muito preenchida é "
                  "uma forma que reaparece em bancadas independentes — é isso "
                  "que a tese central chama de «forma que transfere». O que a "
                  "figura NÃO mostra, de propósito, é o VALOR das constantes: "
                  "eles diferem entre fontes, e essa é a outra metade da tese "
                  "(«constantes são por par tribológico / por bancada»). Os "
                  "valores estão tabelados no volume 1 do Manual, com "
                  "procedência."),
    )


NOMES = ["fig1_anatomia", "fig2_decomposicao", "fig3_painel", "fig4_tornado",
         "fig5_formas_fontes"]
ARTEFATOS = [f"{n}{suf}.svg" for n in NOMES for suf in ("", "-dark")]
ARTEFATOS.append("numbers.json")


def _renderiza(store, reg, cs: dict, cid1: str, regra1: str) -> dict:
    """Renderiza as 5 figuras em claro+escuro e devolve o dict `figuras`.

    Escreve em `OUT_DIR` (SVG) ou em `_INSPECAO` (PNG) — quem decide e' o
    `_salva`. Extraida de `main` para que o gate `--check` possa re-renderizar
    num tmpdir SEM duplicar o laco: um gate que compara contra uma segunda copia
    do codigo de render nao compara nada.
    """
    figs: dict = {}
    for modo in ("light", "dark"):
        f1 = fig1(store, reg, modo, cid1)
        f2 = fig2(store, reg, modo, cid1)
        f3 = fig3(store, reg, modo, cs)
        f4 = fig4(modo)
        f5 = fig5(reg, modo)
        if modo == "light":
            f1["regra_de_escolha"] = regra1
            figs = {"fig1": f1, "fig2": f2, "fig3": f3, "fig4": f4, "fig5": f5}
    return figs


def _escreve_numbers(cs: dict, figs: dict) -> dict:
    """Escreve `numbers.json` em `OUT_DIR` e devolve o payload."""
    payload = dict(
        _nota=("Gerado por scripts/manual_figs.py a partir do store canônico. "
               "NÃO editar à mão: o Manual cita estes números, e o gate da F6 "
               "exige que eles venham do store real."),
        engine_fingerprint=cs["fingerprints"][0] if cs["fingerprints"] else None,
        censo=cs, figuras=figs)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # newline="\n" pelo mesmo motivo do _salva: `*.json text eol=lf` no
    # .gitattributes, e `write_text` traduziria \n -> \r\n no Windows.
    with open(OUT_DIR / "numbers.json", "w", encoding="utf-8",
              newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    return payload


# --------------------------------------------------------------------------
def main() -> int:
    global _INSPECAO, OUT_DIR
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dump", action="store_true",
                    help="só imprime os números, sem escrever nada")
    ap.add_argument("--check", action="store_true",
                    help="gate (C): re-renderiza num tmpdir e exige os 11 "
                         "artefatos byte-identicos aos do disco")
    ap.add_argument("--png", metavar="DIR",
                    help="renderiza PNG num diretorio de INSPECAO (nao mexe nos "
                         "SVGs nem no numbers.json) — para olhar a figura")
    a = ap.parse_args()
    if a.png:
        _INSPECAO = Path(a.png)

    store, reg = carrega_store(), carrega_registry()
    cs = censo(store, reg)

    if a.check:
        # ------------------------------------------------------------------
        # GATE (C) — decisao do professor, 2026-07-28.
        #
        # O GATE S6 exige "figuras por script versionado; toda afirmacao
        # numerica sai do store real". Existencia nao prova nenhuma das duas, e
        # isso NAO e' hipotetico: em 2026-07-28 este gate (que ate entao so
        # testava existencia) PASSOU sobre um numbers.json que nomeava PNGs
        # inexistentes (clobber do `--png`) e sobre 10 SVGs QUATRO revisoes de
        # script atrasados. Gate que passa no estado corrompido e' decoracao.
        #
        # (C) re-renderiza tudo num tmpdir e exige byte-identidade dos 11
        # artefatos. E' a unica forma de provar "o que esta no disco E' o que
        # este script + este store produzem" — que e' literalmente o texto do
        # gate. Custa ~12 s, e so e' viavel porque a saida ja e' deterministica
        # (`_salva` passa `metadata={"Date": None}`; sem isso o matplotlib
        # estamparia a data de criacao dentro do SVG e todo artefato "diferiria").
        # ------------------------------------------------------------------
        falta = [n for n in ARTEFATOS if not (OUT_DIR / n).exists()]
        if falta:
            print("FALTA:", ", ".join(falta))
            return 1
        cid1, regra1 = escolhe_caso_anatomia(store, reg)
        canon = OUT_DIR
        with tempfile.TemporaryDirectory(prefix="manual_figs_check_") as td:
            OUT_DIR = Path(td)
            try:
                _escreve_numbers(cs, _renderiza(store, reg, cs, cid1, regra1))
                difere = [n for n in ARTEFATOS
                          if (canon / n).read_bytes() != (OUT_DIR / n).read_bytes()]
            finally:
                OUT_DIR = canon
        if difere:
            print(f"DEFASADO — {len(difere)} de {len(ARTEFATOS)} artefato(s) NAO "
                  f"sao o que este script + o store produzem agora:")
            for n in difere:
                print(f"   {n}")
            print("   -> regere com `py -3.12 scripts/manual_figs.py` (sem flags).")
            return 1
        fp = cs["fingerprints"][0] if cs["fingerprints"] else "?"
        print(f"OK — gate (C): {len(ARTEFATOS)} artefatos byte-identicos ao que "
              f"o script + o store {fp} produzem agora "
              f"({OUT_DIR.relative_to(ROOT)})")
        return 0

    cid1, regra1 = escolhe_caso_anatomia(store, reg)
    if a.dump:
        print(json.dumps(cs, ensure_ascii=False, indent=2))
        print(f"\ncaso da fig.1: {cid1}  (regra: {regra1})")
        return 0

    figs = _renderiza(store, reg, cs, cid1, regra1)

    if _INSPECAO is not None:
        # O `--help` do `--png` promete "nao mexe nos SVGs nem no numbers.json"
        # — e ate 2026-07-28 ele MENTIA sobre a segunda metade: `main` escrevia
        # o numbers.json CANONICO em qualquer modo, e como `arquivo` vem de
        # `_salva` (que troca .svg -> .png no modo inspecao), o arquivo passava
        # a apontar para PNGs que nao estao em `figs/`. MEDIDO: a 4a rodada de
        # inspecao (08:05:21 de 2026-07-28, ultima escrita antes da maquina
        # cair) deixou exatamente esse estado. Falha silenciosa classica: o modo
        # "somente olhar" corrompia o artefato que o Manual cita.
        print(f"INSPECAO — 10 PNGs em {_INSPECAO}")
        print("   SVGs e numbers.json NAO tocados (por design deste modo).")
        return 0

    payload = _escreve_numbers(cs, figs)

    print(f"OK — 10 SVGs (claro+escuro) + numbers.json em "
          f"{OUT_DIR.relative_to(ROOT)}")
    print(f"   censo: {cs['n_tripe']}/{cs['n_comparaveis']} no tripé "
          f"({cs['pct_tripe']} %) · mediana {cs['mae_mediana']} · "
          f"fingerprint {payload['engine_fingerprint']}")
    print(f"   fig.1/2 usam {cid1}  (regra: {regra1})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
