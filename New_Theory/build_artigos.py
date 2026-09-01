# -*- coding: utf-8 -*-
"""Gera as páginas por ARTIGO e as visões GLOBAIS, em `New_Theory/metodologia/`.

Pedidos do professor em 2026-08-25, nesta ordem:

1. **`artigo_<FONTE>.html`** (uma por fonte) — todas as curvas, os erros por
   perna, a decomposição por mecanismo e as constantes com procedência.
2. **`global_tipos.html`** — comportamento MÉDIO do modelo por tipo de curva:
   axial × transversal, por diâmetro, por atrito, por mecanismo dominante.
3. **`global_parametros.html`** — o efeito dos parâmetros (tornado OAT do
   `knowledge_base`, que já mede sensibilidade por família).
4. **`fluxo.html`** — fluxograma de uso do projeto, do PDF à adoção.
5. **`modelo_nao_fit.html`** — uma fonte, **constantes idênticas**, dois
   comportamentos opostos. É a demonstração de que é modelo e não ajuste.

Reusa `plot`/`expl`/`pagina` de `build_metodologia.py` — um só estilo de página.

    py -3.12 New_Theory/build_artigos.py
"""
from __future__ import annotations

import collections
import html as _esc
import itertools
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "New_Theory"))

import numpy as np  # noqa: E402

import bolt_analysis_studio.validation.report_html as rh  # noqa: E402
import bolt_analysis_studio.validation.runner as rn  # noqa: E402
from bolt_analysis_studio.calibration import knowledge_base as kb  # noqa: E402
from bolt_analysis_studio.validation.case_registry import all_records  # noqa: E402
from bolt_analysis_studio.validation.runner import CaseResult  # noqa: E402

from build_metodologia import SAIDA, carrega, expl, familias, pagina, plot  # noqa: E402

CORES = ("var(--accent)", "var(--warn)", "var(--ok)", "#c86ad0", "#d0a06a",
         "#6ad0c8", "#d06a6a", "#8a9ad0", "#b0d06a", "#d06ab0")
MECS = ("embedding", "creep", "wear", "rotational_loosening", "thread_fretting",
        "fatigue")


def consts_efetivas(rec):
    """cfg do grupo + o `per_case` que casa esta curva."""
    g = rn._adopted_for(rec.source, rec.case_id,
                        getattr(rec.validation_case, "bolt_size", "") or "")
    if not g:
        return "", {}
    c = (kb.adopted_config(g) or {}).get("cfg") or {}
    eff = {k: v for k, v in c.items() if k != "per_case"}
    for tok, d in (c.get("per_case") or {}).items():
        if tok in rec.case_id and isinstance(d, dict):
            eff.update(d)
    return g, eff


def barras_pernas(itens, lim_sd):
    """Uma barra por curva, em MÚLTIPLOS do limite — a única escala em que as
    três pernas são comparáveis entre si (limites diferentes)."""
    if not itens:
        return ""
    w, lw, rw = 860, 250, 70
    bh, gap = 13, 6
    h = len(itens) * (bh + gap) + 30
    vmax = max(max(m / rh.META_MAE, x / rh.META_MAX, (s / lim_sd if s else 0))
               for _c, m, x, s in itens)
    vmax = max(vmax, 1.2)
    o = []
    x1 = ML = lw
    larg = w - lw - rw
    for g in range(4):
        v = vmax * g / 3
        px = ML + v / vmax * larg
        o.append(f'<line x1="{px:.1f}" y1="0" x2="{px:.1f}" y2="{h-22}" '
                 f'class="gl"/>'
                 f'<text x="{px:.1f}" y="{h-8}" text-anchor="middle" class="tk">'
                 f'{v:.1f}x</text>')
    px = ML + 1.0 / vmax * larg
    o.append(f'<line x1="{px:.1f}" y1="0" x2="{px:.1f}" y2="{h-22}" '
             f'style="stroke:var(--warn);stroke-width:1.4;stroke-dasharray:4 3"/>')
    for i, (cid, m, x, s) in enumerate(itens):
        y = i * (bh + gap) + 3
        vals = [(m / rh.META_MAE, "var(--accent)", "MAE"),
                (x / rh.META_MAX, "var(--ok)", "res.máx"),
                ((s / lim_sd) if s else 0.0, "var(--warn)", "σ_res")]
        o.append(f'<text x="{lw-6}" y="{y+bh-3}" text-anchor="end" class="tk">'
                 f'{_esc.escape(cid[-30:])}</text>')
        for j, (v, cor, nome) in enumerate(vals):
            yy = y + j * (bh / 3)
            bl = max(v / vmax * larg, 0.8)
            o.append(f'<rect x="{ML}" y="{yy:.1f}" width="{bl:.1f}" '
                     f'height="{bh/3-0.6:.1f}" style="fill:{cor};fill-opacity:.85">'
                     f'<title>{_esc.escape(cid)} — {nome}: {v:.2f}x o limite</title>'
                     f'</rect>')
    o.append(f'<text x="{ML+4}" y="{h-8}" class="tk">'
             f'azul MAE · verde res.máx · âmbar σ_res — tracejado = o limite</text>')
    return (f'<svg viewBox="0 0 {w} {h}" role="img" '
            f'aria-label="pernas em múltiplos do limite">{"".join(o)}</svg>')


def empilhado(ciclos, series, w=860, h=300):
    """Área empilhada da decomposição por mecanismo."""
    if not series:
        return ""
    ML, MR, MT, MB = 62, 18, 14, 46
    x0, x1 = min(ciclos), max(ciclos)
    if x1 - x0 < 1e-9:
        return ""
    tot = np.sum([s[1] for s in series], axis=0)
    y1 = max(float(np.max(tot)), 1e-9) * 1.06
    X = lambda v: ML + (v - x0) / (x1 - x0) * (w - ML - MR)
    Y = lambda v: MT + (1 - v / y1) * (h - MT - MB)
    o = []
    for g in range(5):
        ty = y1 * g / 4
        o.append(f'<line x1="{ML}" y1="{Y(ty):.1f}" x2="{w-MR}" y2="{Y(ty):.1f}" '
                 f'class="gl"/><text x="{ML-7}" y="{Y(ty)+3:.1f}" '
                 f'text-anchor="end" class="tk">{ty:.3f}</text>')
    base = np.zeros(len(ciclos))
    for i, (nome, vals) in enumerate(series):
        topo = base + vals
        pts = ([f"{X(c):.1f},{Y(v):.1f}" for c, v in zip(ciclos, topo)]
               + [f"{X(c):.1f},{Y(v):.1f}" for c, v in zip(reversed(ciclos),
                                                           reversed(base))])
        o.append(f'<polygon points="{" ".join(pts)}" '
                 f'style="fill:{CORES[i % len(CORES)]};fill-opacity:.72">'
                 f'<title>{_esc.escape(nome)}</title></polygon>')
        base = topo
    lx = ML + 6
    for i, (nome, _v) in enumerate(series):
        o.append(f'<rect x="{lx}" y="{MT+3}" width="9" height="9" rx="2" '
                 f'style="fill:{CORES[i % len(CORES)]}"/>'
                 f'<text x="{lx+13}" y="{MT+11.5}" class="tk">'
                 f'{_esc.escape(nome)}</text>')
        lx += 22 + len(nome) * 5.6
    o.append(f'<text x="{(ML+w-MR)/2:.0f}" y="{h-6}" text-anchor="middle" '
             f'class="tk">ciclo</text>')
    return (f'<svg viewBox="0 0 {w} {h}" role="img" '
            f'aria-label="decomposição por mecanismo">{"".join(o)}</svg>')


# --------------------------------------------------------------------------- #
# 1. Uma pagina por ARTIGO                                                    #
# --------------------------------------------------------------------------- #

def pagina_artigo(fonte, comp, res, pisos, store, tem_repl) -> str:
    curvas = sorted([r for r in comp if r.source == fonte], key=lambda r: r.case_id)
    lim_sd = rh.limite_sres(fonte, pisos)
    piso = pisos["por_fonte"].get(fonte)

    # --- todas as curvas: dado (pontos) e modelo (linha) ------------------
    ser = []
    for i, r in enumerate(curvas):
        rr = res.get(r.case_id)
        if rr is None or not getattr(rr, "metric_x", None):
            continue
        cor = CORES[i % len(CORES)]
        rot = r.case_id.replace(fonte.lower().replace("_", ""), "")[-18:]
        ser.append((np.asarray(rr.metric_x, float),
                    np.asarray(rr.metric_data, float), rot, cor, "ponto"))
        ser.append((np.asarray(rr.metric_x, float),
                    np.asarray(rr.metric_pred, float), "", cor, "linha"))
    ser = [s for s in ser if len(s[0])]
    logx = False
    if ser:
        xs = [x for s in ser for x in s[0] if x > 0]
        logx = bool(xs) and (max(xs) / max(min(xs), 1.0) > 400)
    p_curvas = plot(ser, "ciclo" + (" (log)" if logx else ""), "F/F₀", h=380,
                    logx=logx)

    # --- erros por perna, em multiplos do limite ---------------------------
    itens = []
    for r in curvas:
        rr = res.get(r.case_id)
        if rr is None:
            continue
        sd = rh.sres_para_censo(rr)
        itens.append((r.case_id, float(rr.mae), float(rr.maxerr),
                      float(sd) if sd is not None else 0.0))
    p_erros = barras_pernas(itens, lim_sd)

    # --- decomposicao por mecanismo: MEDIA da fonte ------------------------
    recs = store.get("cases", store)
    acum = {}
    ncur = 0
    grade = None
    for r in curvas:
        d = (recs.get(r.case_id) or {}).get("decomp") or {}
        cyc = (recs.get(r.case_id) or {}).get("cycles") or []
        if not d or not cyc:
            continue
        u = np.linspace(0.0, 1.0, 60)
        xc = np.asarray(cyc, float)
        if xc.max() <= 0:
            continue
        grade = u
        for m in MECS:
            v = d.get(m)
            if not isinstance(v, list) or len(v) != len(cyc):
                continue
            acum[m] = acum.get(m, np.zeros(60)) + np.interp(u * xc.max(), xc,
                                                            np.asarray(v, float))
        ncur += 1
    p_dec = ""
    dom = ""
    if acum and ncur and grade is not None:
        med = [(m, acum[m] / ncur) for m in MECS if m in acum
               and float(np.max(acum[m])) > 1e-12]
        if med:
            fim = {m: float(v[-1]) for m, v in med}
            tot = sum(fim.values()) or 1.0
            dom = " · ".join(f"<b>{m}</b> {100*v/tot:.0f}&nbsp;%"
                             for m, v in sorted(fim.items(), key=lambda q: -q[1]))
            p_dec = empilhado(list(grade), med)

    # --- tabela + constantes ----------------------------------------------
    linhas = []
    n_ok = 0
    for r in curvas:
        rr = res.get(r.case_id)
        if rr is None:
            continue
        sd = rh.sres_para_censo(rr)
        ok = rh._tripe_ok(rr, lim_sd)
        n_ok += 1 if ok else 0
        est = ("no tripé" if ok else
               ("exceção" if r.case_id in rh._EXCECOES else
                ("declarada" if r.case_id in getattr(rh, "_DECLARADAS", {})
                 else "fora")))
        linhas.append(
            f'<tr><td><code>{_esc.escape(r.case_id)}</code></td>'
            f'<td class="n">{rr.mae:.4f}</td><td class="n">{rr.maxerr:.4f}</td>'
            f'<td class="n">{"—" if sd is None else f"{sd:.4f}"}</td>'
            f'<td>{est}</td></tr>')

    grupos = {}
    for r in curvas:
        g, eff = consts_efetivas(r)
        if g and g not in grupos:
            grupos[g] = eff
    kl = []
    for g, eff in sorted(grupos.items()):
        prov = (kb.adopted_config(g) or {}).get("prov") or {}
        num = {k: v for k, v in sorted(eff.items())
               if isinstance(v, (int, float)) and not isinstance(v, bool)}
        cel = " · ".join(
            f'<code>{_esc.escape(k)}</code>={v:.4g}'
            + ("" if k in prov else " <span class=\"sub\">(sem proc.)</span>")
            for k, v in list(num.items())[:14])
        kl.append(f'<tr><td><code>{_esc.escape(g)}</code></td>'
                  f'<td class="n">{len(num)}</td><td>{cel or "—"}</td></tr>')
    n_sem = sum(1 for g, eff in grupos.items()
                for k, v in eff.items()
                if isinstance(v, (int, float)) and not isinstance(v, bool)
                and k not in ((kb.adopted_config(g) or {}).get("prov") or {}))
    n_tot_k = sum(1 for eff in grupos.values() for v in eff.values()
                  if isinstance(v, (int, float)) and not isinstance(v, bool))

    link_repl = (f'<p class="nav"><a href="replicas_{fonte}.html">'
                 f'&rarr; modelo contra as réplicas desta fonte</a></p>'
                 if tem_repl else "")
    piso_txt = ("sem piso medido (sem família de réplica válida)" if piso is None
                else f"MAE <b>{piso[0]:.4f}</b> · res.máx <b>{piso[1]:.4f}</b> · "
                     f"σ <b>{piso[2]:.4f}</b>")

    corpo = f"""
<h1>{_esc.escape(fonte)}</h1>
<p class="sub"><b>{len(curvas)}</b> curvas · <b>{n_ok}</b> no tripé ·
limite de σ_res desta fonte <b>{lim_sd:.4f}</b> ·
piso de repetibilidade: {piso_txt}.</p>
<p class="nav"><a href="index.html">&larr; metodologia</a> ·
<a href="global_tipos.html">visão global</a></p>
{link_repl}

<h2>Todas as curvas</h2>
{p_curvas}
{expl('os <b>pontos</b> são o dado digitalizado e as <b>linhas</b> a previsão do '
      'modelo, uma cor por curva.',
      'o que se lê aqui é a <b>família inteira</b> de uma vez: onde as curvas se '
      'separam, o modelo tem de separar junto. Cada par cor-ponto/cor-linha é uma '
      'condição — se a linha acompanha os pontos da mesma cor em todas, uma '
      'física só está cobrindo o conjunto.',
      f'<b>{len(curvas)}</b> curvas, <b>{n_ok}</b> no tripé '
      f'({100*n_ok//max(len(curvas),1)}&nbsp;%).')}

<h2>Erro por perna, em múltiplos do limite</h2>
{p_erros}
{expl('as três pernas de cada curva, cada uma dividida pelo <b>seu</b> limite.',
      'é a única escala em que as três são comparáveis: os limites são '
      'diferentes (0,05 · 0,10 · o da fonte), então valores absolutos não se '
      'comparam. Passar do tracejado é reprovar naquela perna.',
      f'limite de σ_res usado: <b>{lim_sd:.4f}</b> — '
      f'{"o global" if abs(lim_sd - rh.META_SRES) < 1e-9 else "o piso da fonte (D1)"}.')}

{'<h2>Por onde o modelo perde pré-carga</h2>' + p_dec + expl(
    'a perda de pré-carga acumulada, separada por mecanismo, em <b>média</b> '
    'sobre as curvas da fonte; o eixo x é a fração da vida de cada ensaio.',
    'a espessura de cada faixa é quanto aquele mecanismo tirou. Uma fonte em que '
    'um mecanismo domina é uma fonte que testa <b>aquele</b> mecanismo — e é '
    'assim que se sabe o que a fonte de fato mede.',
    f'no fim do ensaio: {dom}.') if p_dec else ''}

<h2>As curvas, uma a uma</h2>
<table><tr><th>curva</th><th>MAE</th><th>res.máx</th><th>σ_res</th>
<th>estatuto</th></tr>{''.join(linhas)}</table>

<h2>Constantes adotadas</h2>
<table><tr><th>grupo</th><th>n</th><th>constantes (até 14)</th></tr>
{''.join(kl)}</table>
{expl('os grupos de configuração que servem esta fonte e as constantes que eles '
      'carregam.',
      'quanto <b>menos</b> constantes para <b>mais</b> curvas, mais o resultado é '
      'predição e menos é ajuste. Uma constante marcada <span class="sub">(sem '
      'proc.)</span> não tem procedência declarada — pode ser leitura do paper ou '
      'ajuste, e a página não sabe dizer qual.',
      f'<b>{len(grupos)}</b> grupo(s), <b>{n_tot_k}</b> constantes para '
      f'<b>{len(curvas)}</b> curvas '
      f'(<b>{len(curvas)/max(n_tot_k,1):.2f}</b> curva por constante); '
      f'<b>{n_sem}</b> sem procedência.', aviso=(n_sem > 0))}
"""
    return pagina(fonte, corpo)


# --------------------------------------------------------------------------- #
# 2. Visao GLOBAL por tipo de curva                                           #
# --------------------------------------------------------------------------- #

def pagina_tipos(comp, res, pisos, store) -> str:
    recs = store.get("cases", store)

    def classifica(r):
        rr = res.get(r.case_id)
        cu = (getattr(rr, "config_used", None) or {}) if rr else {}
        vc = r.validation_case
        d = (recs.get(r.case_id) or {}).get("decomp") or {}
        fim = {m: (v[-1] if isinstance(v, list) and v else 0.0)
               for m, v in d.items()}
        mec = max(fim, key=fim.get) if fim and max(fim.values()) > 0 else "(sem perda)"
        return dict(
            modo=("transversal (deslocamento)" if cu.get("mode") == "displacement"
                  else "axial / força"),
            diam=(getattr(vc, "bolt_size", "") or "?").split("x")[0],
            mu=f'μ = {float(cu.get("mu") or 0):.3f}',
            mec=mec)

    def bloco(eixo, titulo, como, minimo=3):
        grupos = collections.defaultdict(list)
        for r in comp:
            rr = res.get(r.case_id)
            if rr is None or not getattr(rr, "metric_x", None):
                continue
            grupos[classifica(r)[eixo]].append(r.case_id)
        grupos = {k: v for k, v in grupos.items() if len(v) >= minimo}
        if not grupos:
            return ""
        ser = []
        tab = []
        for i, (k, cids) in enumerate(sorted(grupos.items(),
                                             key=lambda q: -len(q[1]))):
            u = np.linspace(0.02, 1.0, 60)
            Y, MAE, OK = [], [], 0
            for c in cids:
                rr = res[c]
                x = np.asarray(rr.metric_x, float)
                if x.max() <= 0:
                    continue
                Y.append(np.interp(u * x.max(), x, np.asarray(rr.metric_data, float)))
                MAE.append(float(rr.mae))
                fonte = next(q.source for q in comp if q.case_id == c)
                OK += 1 if rh._tripe_ok(rr, rh.limite_sres(fonte, pisos)) else 0
            if not Y:
                continue
            ser.append((u, np.mean(Y, axis=0), f"{k} ({len(cids)})",
                        CORES[i % len(CORES)], "linha"))
            tab.append((k, len(cids), OK, float(np.median(MAE))))
        if not ser:
            return ""
        linhas = "".join(
            f'<tr><td>{_esc.escape(str(k))}</td><td class="n">{n}</td>'
            f'<td class="n">{o}</td><td class="n">{100*o//max(n,1)}&nbsp;%</td>'
            f'<td class="n">{m:.4f}</td></tr>'
            for k, n, o, m in sorted(tab, key=lambda q: -q[1]))
        melhor = max(tab, key=lambda q: q[2] / max(q[1], 1))
        pior = min(tab, key=lambda q: q[2] / max(q[1], 1))
        return (f'<h2>{titulo}</h2>'
                + plot(ser, "fração da vida do ensaio", "F/F₀ médio", h=320)
                + expl('a curva <b>média</b> de cada classe, com cada ensaio '
                       'posto na sua própria fração de vida — em ciclo absoluto '
                       'a média misturaria ensaios de durações diferentes.',
                       como,
                       f'melhor classe: <b>{_esc.escape(str(melhor[0]))}</b> '
                       f'({melhor[2]}/{melhor[1]}); pior: '
                       f'<b>{_esc.escape(str(pior[0]))}</b> '
                       f'({pior[2]}/{pior[1]}).')
                + f'<table><tr><th>classe</th><th>curvas</th><th>no tripé</th>'
                  f'<th>%</th><th>MAE mediano</th></tr>{linhas}</table>')

    b1 = bloco("modo", "Por modo de carregamento: axial × transversal",
               'a queda transversal é dirigida por <b>escorregamento</b> e a '
               'axial por <b>fluência e assentamento</b> — são físicas '
               'diferentes do mesmo engine, e a diferença entre as duas médias é '
               'o quanto o modo importa.')
    b2 = bloco("diam", "Por diâmetro do parafuso",
               'o diâmetro entra na rigidez do parafuso e na área de contato. Se '
               'as médias se separam por tamanho, há efeito de escala; se não, o '
               'que muda é a condição de ensaio, não o tamanho.')
    b3 = bloco("mu", "Por coeficiente de atrito adotado",
               'μ é o parâmetro de <b>maior</b> sensibilidade medida do modelo. '
               'As classes aqui não são um experimento — são os valores que cada '
               'rig recebeu —, então leia como "onde cada μ foi usado", não como '
               '"o efeito de μ".', minimo=6)
    b4 = bloco("mec", "Por mecanismo dominante",
               'qual dos seis mecanismos tirou mais pré-carga. É a classificação '
               '<b>do modelo</b>, não do artigo: diz o que o engine acha que '
               'aconteceu, e por isso é a mais útil para achar onde ele erra.')

    aviso = expl(
        'os quatro eixos acima são os que o registry <b>sustenta</b>: modo, '
        'diâmetro, μ e mecanismo dominante.',
        '⚠️ <b>Material e lubrificação ficaram de fora de propósito.</b> O campo '
        '<code>specimen_label</code> está preenchido em apenas <b>49 das '
        '207</b> curvas, e mistura travamento, pré-carga e geometria; '
        '<code>lubricated</code> é verdadeiro em <b>3</b>. Classificar por '
        'material com esse suporte produziria classes de 2 e 3 curvas e uma '
        'aparência de resultado onde não há dado.',
        'o que existe hoje para material está no <code>specimen_label</code> por '
        'fonte — JCSR (galv/plain/stainless) e ROUSSEAU (steel/hdpe) — e aparece '
        'nas páginas por artigo.', aviso=True)

    return pagina("Comportamento médio por tipo de curva",
                  f'<h1>Comportamento médio do modelo, por tipo de curva</h1>'
                  f'<p class="sub">Cada linha é a média de uma classe, com os '
                  f'ensaios postos na própria fração de vida. '
                  f'<b>{len(comp)}</b> curvas (todas as do documento; o censo publicado usa as <b>comparáveis</b>).</p>'
                  f'<p class="nav"><a href="index.html">&larr; metodologia</a></p>'
                  f'{b1}{b2}{b3}{b4}<h2>O que ficou de fora, e por quê</h2>{aviso}')


# --------------------------------------------------------------------------- #
# 3. Efeito dos PARAMETROS                                                    #
# --------------------------------------------------------------------------- #

def pagina_parametros() -> str:
    fams = ["transverse", "axial", None]
    blocos = []
    for fam in fams:
        try:
            s = kb.sensitivity(fam)
        except Exception:
            continue
        if not s:
            continue
        itens = sorted(((k, v.get("mean", 0.0), v.get("max", 0.0), v.get("n", 0))
                        for k, v in s.items()), key=lambda q: -q[1])
        vmax = max((i[2] for i in itens), default=0.0) or 1.0
        w, lw, rw, bh, gap = 860, 210, 96, 14, 6
        h = len(itens) * (bh + gap) + 26
        o = []
        for g in range(5):
            v = vmax * g / 4
            px = lw + v / vmax * (w - lw - rw)
            o.append(f'<line x1="{px:.1f}" y1="0" x2="{px:.1f}" y2="{h-20}" '
                     f'class="gl"/><text x="{px:.1f}" y="{h-6}" '
                     f'text-anchor="middle" class="tk">{v:.3f}</text>')
        for i, (k, me, mx, n) in enumerate(itens):
            y = i * (bh + gap) + 3
            bm = max((mx / vmax) * (w - lw - rw), 1.0)
            bmed = max((me / vmax) * (w - lw - rw), 0.8)
            morto = mx <= 1e-12
            o.append(
                f'<text x="{lw-6}" y="{y+bh-3}" text-anchor="end" class="tk">'
                f'{_esc.escape(k)}</text>'
                f'<rect x="{lw}" y="{y}" width="{bm:.1f}" height="{bh}" rx="3" '
                f'style="fill:var(--mut);fill-opacity:.25"><title>{_esc.escape(k)}'
                f': máx {mx:.4f}</title></rect>'
                f'<rect x="{lw}" y="{y}" width="{bmed:.1f}" height="{bh}" rx="3" '
                f'style="fill:{"var(--mut)" if morto else "var(--accent)"};'
                f'fill-opacity:.85"><title>{_esc.escape(k)}: média {me:.4f} '
                f'(n={n})</title></rect>'
                f'<text x="{lw+bm+6:.1f}" y="{y+bh-3}" class="tk">'
                f'{"inerte" if morto else f"{me:.4f}"}</text>')
        svg = (f'<svg viewBox="0 0 {w} {h}" role="img" '
               f'aria-label="sensibilidade por parâmetro">{"".join(o)}</svg>')
        mortos = [i[0] for i in itens if i[2] <= 1e-12]
        vivos = [i for i in itens if i[2] > 1e-12]
        nome = {"transverse": "transversal", "axial": "axial"}.get(fam, "todas")
        blocos.append(
            f'<h2>Família <b>{nome}</b></h2>{svg}'
            + expl(
                'cada barra é um parâmetro do <code>JointMaterial</code>: a barra '
                'sólida é o efeito <b>médio</b> sobre a curva e a clara é o '
                '<b>máximo</b>, medidos um-de-cada-vez (OAT) pelo '
                '<code>knowledge_base</code>.',
                'a ordem é a resposta a "qual parâmetro importa aqui". '
                'Parâmetro no topo move a curva; parâmetro marcado '
                '<b>inerte</b> não a move em <b>nenhuma</b> dose — não é que '
                'importe pouco, é que naquele regime o canal dele está fechado.',
                f'<b>{len(vivos)}</b> parâmetros com efeito e <b>{len(mortos)}</b> '
                f'inertes nesta família'
                + (f': <code>{"</code> · <code>".join(_esc.escape(m) for m in mortos[:8])}</code>.'
                   if mortos else '.')))
    try:
        frozen = kb.frozen_params()
    except Exception:
        frozen = {}
    fz = ""
    if frozen:
        fz = ('<h2>Parâmetros CONGELADOS</h2>'
              + '<table><tr><th>parâmetro</th><th>razão</th></tr>'
              + "".join(f'<tr><td><code>{_esc.escape(k)}</code></td>'
                        f'<td>{_esc.escape(str(v))}</td></tr>'
                        for k, v in sorted(frozen.items())) + '</table>'
              + expl('os parâmetros que o projeto proíbe de fitar.',
                     'sensibilidade ≈ 0 medida: fitá-los seria ajustar ruído, e '
                     'pior — daria a impressão de grau de liberdade onde não há. '
                     'O registro os bloqueia no otimizador.',
                     f'<b>{len(frozen)}</b> congelados.'))
    return pagina("Efeito dos parâmetros",
                  f'<h1>Efeito dos parâmetros</h1>'
                  f'<p class="sub">Sensibilidade um-de-cada-vez medida pelo '
                  f'<code>knowledge_base</code>, por família de carregamento. '
                  f'Para a curva ao vivo de cada parâmetro, com slider, veja o '
                  f'<a href="../variable_explorer/index.html">Explorador de '
                  f'Variáveis</a> (129 páginas, uma por campo).</p>'
                  f'<p class="nav"><a href="index.html">&larr; metodologia</a></p>'
                  f'{"".join(blocos)}{fz}')


# --------------------------------------------------------------------------- #
# 4. Fluxograma de uso do projeto                                             #
# --------------------------------------------------------------------------- #

def caixa(x, y, w, h, titulo, linhas, cor="var(--accent)"):
    o = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" '
         f'style="fill:var(--card);stroke:{cor};stroke-width:1.6"/>'
         f'<text x="{x+w/2:.0f}" y="{y+17}" text-anchor="middle" '
         f'style="fill:{cor};font-size:12px;font-weight:600">'
         f'{_esc.escape(titulo)}</text>']
    for i, l in enumerate(linhas):
        o.append(f'<text x="{x+10}" y="{y+34+i*13}" class="tk">{_esc.escape(l)}</text>')
    return "".join(o)


def seta(x1, y1, x2, y2, rot=""):
    o = [f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
         f'style="stroke:var(--mut);stroke-width:1.6" marker-end="url(#pt)"/>']
    if rot:
        o.append(f'<text x="{(x1+x2)/2+6:.0f}" y="{(y1+y2)/2-4:.0f}" '
                 f'class="tk">{_esc.escape(rot)}</text>')
    return "".join(o)


def pagina_fluxo(comp, res, pisos) -> str:
    # ⚠️ CENSO pelo filtro CANONICO `caso_comparavel`, nao por
    # `caso_no_documento`. A docstring dele diz "filtro UNICO do censo de
    # comparaveis — todo consumidor passa por aqui"; contar por fora publicava
    # 173/207 ao lado do canonico 171/205, que e o §4.43 na forma mais direta:
    # numero de censo por caminho proprio, divergindo em 2.
    cens = [r for r in comp if rh.caso_comparavel(r.source, r.case_id)]
    n_fonte = len({r.source for r in cens})
    n_ok = sum(1 for r in cens
               if rh._tripe_ok(res.get(r.case_id), rh.limite_sres(r.source, pisos)))
    W, H = 860, 760
    d = ['<defs><marker id="pt" viewBox="0 0 10 10" refX="9" refY="5" '
         'markerWidth="6" markerHeight="6" orient="auto">'
         '<path d="M0,0 L10,5 L0,10 z" style="fill:var(--mut)"/></marker></defs>']
    d.append(caixa(30, 20, 240, 74, "1. PDF do artigo",
                   ["BAS_V2_papers/", "figura recortada ->", "paper_figures/*.png"]))
    d.append(caixa(310, 20, 240, 74, "2. Digitalização",
                   ["leitura manual do traço", "-> digitized_csv/*.csv",
                    "+ nota de aparato"]))
    d.append(caixa(590, 20, 240, 74, "3. Registry",
                   ["core/validation_cases.py", "ValidationCase: inputs",
                    "offset/scale, varreduras"]))
    d.append(seta(270, 57, 308, 57))
    d.append(seta(550, 57, 588, 57))
    d.append(caixa(590, 140, 240, 88, "4. Runner",
                   ["validation/runner.py", "simula ciclo a ciclo",
                    "alinha, aplica FLOOR_TRIM", "e trim_n_max"], "var(--ok)"))
    d.append(seta(710, 96, 710, 138))
    d.append(caixa(310, 140, 240, 88, "5. Store",
                   ["validation_store.json", "metric_x / data / pred",
                    "decomp por mecanismo", "engine_fingerprint"], "var(--ok)"))
    d.append(seta(588, 184, 552, 184))
    d.append(caixa(30, 140, 240, 88, "6. Report",
                   ["validation/report_html.py", "três pernas por curva",
                    "piso por fonte (D1)", "censo publicado"], "var(--ok)"))
    d.append(seta(308, 184, 272, 184))
    d.append(caixa(30, 274, 240, 88, "7. Triagem",
                   ["regra_de_parada_triagem", "classifica as fora:",
                    "form-limited, declarada,", "exceção, indecidível"],
                   "var(--warn)"))
    d.append(seta(150, 230, 150, 272))
    d.append(caixa(310, 274, 240, 88, "8. Ataque da curva",
                   ["ataque_curva.py", "varre alavancas", "mede o que move",
                    "e o que é inerte"], "var(--warn)"))
    d.append(seta(272, 318, 308, 318))
    d.append(caixa(590, 274, 240, 88, "9. PRÉ-REGISTRO",
                   ["specs/*-prereg.md", "gates IMUTÁVEIS", "predições ANTES",
                    "ramo INCONCLUSIVO"], "var(--warn)"))
    d.append(seta(552, 318, 588, 318))
    d.append(caixa(590, 408, 240, 88, "10. Execução",
                   ["mede contra os gates", "gate vermelho = fica",
                    "vermelho; não se move", "a trave depois de ver"],
                   "#c86ad0"))
    d.append(seta(710, 364, 710, 406))
    d.append(caixa(310, 408, 240, 88, "11. Adoção",
                   ["adopted_configs.json", "single-writer", "re-carimba o store",
                    "fingerprint novo"], "#c86ad0"))
    d.append(seta(588, 452, 552, 452))
    d.append(caixa(30, 408, 240, 88, "12. Re-geração",
                   ["report + explorador", "números recomputados",
                    "guardas de envelhecimento", "acusam o vencido"],
                   "#c86ad0"))
    d.append(seta(308, 452, 272, 452))
    d.append(f'<path d="M30 452 L14 452 L14 184 L28 184" fill="none" '
             f'style="stroke:var(--mut);stroke-width:1.4;stroke-dasharray:5 4" '
             f'marker-end="url(#pt)"/>'
             f'<text x="20" y="320" class="tk" transform="rotate(-90 20 320)" '
             f'text-anchor="middle">o ciclo recomeça</text>')
    d.append(caixa(30, 546, 800, 96, "REGRAS QUE ATRAVESSAM TODAS AS ETAPAS",
                   ["· prereg com gates escritos ANTES de medir — gate vermelho fica vermelho",
                    "· número publicado carrega a definição; guardas acusam número vencido",
                    "· constante nova precisa de PROCEDÊNCIA: lida do paper, de norma, ou declarada como fit",
                    "· o veredito é por CURVA; leituras por condição são diagnóstico, não porta",
                    "· adoção é single-writer: uma sessão escreve, as outras medem"],
                   "var(--mut)"))
    d.append(f'<text x="{W/2:.0f}" y="{H-14}" text-anchor="middle" class="tk">'
             f'{len(cens)} curvas comparáveis · {n_fonte} fontes · '
             f'{n_ok} no tripé</text>')
    svg = (f'<svg viewBox="0 0 {W} {H}" role="img" '
           f'aria-label="fluxo do projeto, do PDF à adoção">{"".join(d)}</svg>')
    return pagina("Fluxo de uso do projeto",
                  f'<h1>Fluxo de uso do projeto</h1>'
                  f'<p class="sub">Do PDF do artigo até a adoção de uma constante '
                  f'— e de volta.</p>'
                  f'<p class="nav"><a href="index.html">&larr; metodologia</a></p>'
                  f'{svg}'
                  + expl('as doze etapas e os arquivos onde cada uma vive.',
                         'as caixas <b>azuis</b> trazem dado para dentro; as '
                         '<b>verdes</b> medem; as <b>âmbar</b> decidem o que '
                         'atacar e registram a aposta; as <b>roxas</b> mudam o '
                         'estado do projeto. A seta pontilhada à esquerda é o que '
                         'torna isto um ciclo: toda adoção volta ao report.',
                         f'hoje: <b>{len(cens)}</b> curvas comparáveis de '
                         f'<b>{n_fonte}</b> fontes, <b>{n_ok}</b> no tripé — '
                         f'contado pelo filtro canônico '
                         f'<code>caso_comparavel</code>, o mesmo do censo '
                         f'publicado.'))



# --------------------------------------------------------------------------- #
# 5. MODELO, nao fit — mesmas constantes, comportamentos opostos              #
# --------------------------------------------------------------------------- #

def pagina_modelo_nao_fit(comp, res, pisos) -> str:
    """A demonstracao: UMA fisica, N comportamentos.

    O par foi escolhido por MEDICAO — varri todos os pares de curvas cujas
    constantes efetivas (grupo + `per_case`) sao IDENTICAS e ordenei pela
    diferenca de retencao final.

    ⚠️ O candidato obvio foi FALSIFICADO no caminho: o aco do `ROUSSEAU_2025`
    (t10/t12/t14) parecia o exemplo perfeito — mesma fonte, espessuras
    diferentes, colapso contra travamento — mas medindo as constantes efetivas,
    **10 campos diferem** entre as espessuras via `per_case`. Nao serve para
    afirmar "mesma fisica", e usa-lo seria exatamente o erro que esta pagina
    existe para negar.
    """
    porid = {r.case_id: r for r in comp}
    # todas as fig18 do LU_2024: mesma figura, mesma config, 5 amplitudes
    fam = sorted([c for c in porid
                  if c.startswith("lu2024_M8_fig18_amp")
                  and res.get(c) is not None
                  and getattr(res[c], "metric_x", None)])
    if len(fam) < 3:
        return ""
    # ⚠️ So' o MAIOR subconjunto que COMPARTILHA as constantes. A familia
    # inteira da fig18 NAO compartilha (medido: a pagina chegou a imprimir
    # "constantes efetivas DIFERENTES entre as 5 curvas" ao lado de uma prosa
    # dizendo "a mesma configuracao") — e afirmar numa pagina o contrario do que
    # ela mede e' o defeito que esta pagina existe para negar.
    por_sig = collections.defaultdict(list)
    for c in fam:
        _g, eff = consts_efetivas(porid[c])
        por_sig[json.dumps({k: str(v) for k, v in sorted(eff.items())},
                           sort_keys=True)].append(c)
    sig, fam = max(por_sig.items(), key=lambda q: len(q[1]))
    fam = sorted(fam)
    if len(fam) < 2:
        return ""
    mesma = True
    descartadas = sum(len(v) for k, v in por_sig.items() if k != sig)
    _g0, eff0 = consts_efetivas(porid[fam[0]])
    nk = sum(1 for v in eff0.values()
             if isinstance(v, (int, float)) and not isinstance(v, bool))

    ser, tab = [], []
    for i, c in enumerate(fam):
        rr = res[c]
        amp = float(getattr(porid[c].validation_case,
                            "transverse_displacement_mm", 0) or 0)
        cor = CORES[i % len(CORES)]
        rot = f"{amp:g} mm"
        ser.append((np.asarray(rr.metric_x, float),
                    np.asarray(rr.metric_data, float), rot, cor, "ponto"))
        ser.append((np.asarray(rr.metric_x, float),
                    np.asarray(rr.metric_pred, float), "", cor, "linha"))
        ok = rh._tripe_ok(rr, rh.limite_sres(porid[c].source, pisos))
        tab.append((rot, c, float(rr.metric_data[-1]), float(rr.metric_pred[-1]),
                    float(rr.mae), bool(ok)))
    tab.sort(key=lambda q: -q[2])
    linhas = "".join(
        f'<tr><td>{_esc.escape(a)}</td><td><code>{_esc.escape(c)}</code></td>'
        f'<td class="n">{d:.3f}</td><td class="n">{p:.3f}</td>'
        f'<td class="n">{m:.4f}</td><td>{"no tripé" if o else "fora"}</td></tr>'
        for a, c, d, p, m, o in tab)
    espalha = tab[0][2] - tab[-1][2]
    n_ok = sum(1 for t in tab if t[5])

    # --- 2o exemplo: a predicao ZERO-REFIT do ROUSSEAU HDPE ---------------
    z = ""
    par = [c for c in ("rousseau2025_hdpe_t10", "rousseau2025_hdpe_t10_amp0p2")
           if c in porid and res.get(c) is not None]
    if len(par) == 2:
        a, b = par
        sa = consts_efetivas(porid[a])[1]
        sb = consts_efetivas(porid[b])[1]
        iguais = (json.dumps({k: str(v) for k, v in sorted(sa.items())},
                             sort_keys=True)
                  == json.dumps({k: str(v) for k, v in sorted(sb.items())},
                                sort_keys=True))
        s2 = []
        for i, c in enumerate(par):
            rr = res[c]
            amp = float(getattr(porid[c].validation_case,
                                "transverse_displacement_mm", 0) or 0)
            s2.append((np.asarray(rr.metric_x, float),
                       np.asarray(rr.metric_data, float), f"{amp:g} mm",
                       CORES[i], "ponto"))
            s2.append((np.asarray(rr.metric_x, float),
                       np.asarray(rr.metric_pred, float), "", CORES[i], "linha"))
        fa = float(res[a].metric_data[-1])
        fb = float(res[b].metric_data[-1])
        z = ('<h2>Segundo exemplo: predição ZERO-REFIT</h2>'
             + plot(s2, "ciclo", "F/F₀", h=330)
             + expl(
                 f'as duas curvas de HDPE do <code>ROUSSEAU_2025</code>, em '
                 f'amplitudes diferentes. Constantes efetivas '
                 f'<b>{"idênticas" if iguais else "diferentes"}</b>.',
                 'a de amplitude menor é uma <b>condição inédita</b> — foi '
                 'digitalizada depois, e o modelo a previu sem que nenhuma '
                 'constante fosse tocada. Um ajuste não extrapola para fora do '
                 'domínio em que foi ajustado; uma física, sim.',
                 f'retenção final <b>{fa:.3f}</b> contra <b>{fb:.3f}</b> — '
                 f'{abs(fb-fa):.3f} de diferença, com MAE '
                 f'{res[a].mae:.4f} e {res[b].mae:.4f}.'))

    aviso_falso = expl(
        'como o par foi escolhido.',
        'varri <b>todos</b> os pares cujas constantes efetivas (grupo + '
        '<code>per_case</code>) são idênticas, e ordenei pela diferença de '
        'retenção final. ⚠️ O candidato óbvio <b>foi falsificado</b>: o aço do '
        '<code>ROUSSEAU_2025</code> (t10/t12/t14) parecia perfeito — mesma '
        'fonte, espessuras diferentes, colapso contra travamento — mas '
        '<b>10 constantes diferem</b> entre as espessuras via '
        '<code>per_case</code>. Usá-lo seria cometer exatamente o erro que esta '
        'página nega.',
        'o par publicado passou pelo teste que o candidato óbvio reprovou.',
        aviso=True)

    corpo = f"""
<h1>É modelo, não fit</h1>
<p class="sub">Uma física, vários comportamentos — com as <b>mesmas
constantes</b>.</p>
<p class="nav"><a href="index.html">&larr; metodologia</a></p>

<h2>Varredura de amplitude do <code>LU_2024</code> (fig. 18)</h2>
{plot(ser, "ciclo", "F/F₀", h=380)}
{expl('as {n} curvas da mesma figura, em amplitudes de {lo} a {hi}. Os pontos '
      'são o dado, as linhas a previsão.'.format(n=len(fam),
                                                 lo=tab[-1][0], hi=tab[0][0]),
      'a <b>mesma</b> configuração — as mesmas '
      f'{nk} constantes, sem um número por curva — produz desde retenção alta '
      'até colapso quase total. O modelo não foi ajustado a cada curva: ele '
      'recebeu a <b>amplitude</b> como entrada e o resto saiu da física.',
      f'constantes efetivas <b>idênticas</b> entre as {len(fam)} curvas; '
      f'retenção final varia <b>{espalha:.3f}</b> (de {tab[0][2]:.3f} a '
      f'{tab[-1][2]:.3f}) e <b>{n_ok} de {len(fam)}</b> estão no tripé.'
      + (f' ⚠️ Outras <b>{descartadas}</b> curvas da mesma figura ficaram '
         f'<b>fora</b> deste bloco porque suas constantes diferem — incluí-las '
         f'quebraria a afirmação.' if descartadas else ''), aviso=False)}

<table><tr><th>amplitude</th><th>curva</th><th>dado (fim)</th>
<th>modelo (fim)</th><th>MAE</th><th>estatuto</th></tr>{linhas}</table>

{expl('a mesma tabela, lida como argumento.',
      'se fossem ajustes independentes, cada linha teria as suas constantes e '
      'acertar seria trivial — e sem valor. O que se afirma aqui é o contrário: '
      'uma configuração só, e a diferença entre as linhas vem <b>inteira</b> da '
      'entrada que mudou.',
      f'{len(fam)} curvas, 1 configuração, {nk} constantes.')}

{z}

<h2>Como este par foi escolhido</h2>
{aviso_falso}
"""
    return pagina("É modelo, não fit", corpo)


# --------------------------------------------------------------------------- #


# --------------------------------------------------------------------------- #
# 6. QUALIFICACAO — decisao, paridade e cobertura                             #
# --------------------------------------------------------------------------- #

def _svg_paridade(pts, w=860, h=430, lim=0.85):
    """Previsto x observado, com a reta 1:1, bandas e o quadrante PERIGOSO."""
    if not pts:
        return ""
    ML, MR, MT, MB = 62, 18, 14, 46
    X = lambda v: ML + v * (w - ML - MR)
    Y = lambda v: MT + (1 - v) * (h - MT - MB)
    o = []
    # quadrante de falso SEGURO: dado < lim  E  modelo >= lim
    o.append(f'<rect x="{ML}" y="{Y(1.0):.1f}" width="{X(lim)-ML:.1f}" '
             f'height="{Y(lim)-Y(1.0):.1f}" style="fill:var(--warn);'
             f'fill-opacity:.10"/>')
    for g in range(6):
        t = g / 5
        o.append(f'<line x1="{ML}" y1="{Y(t):.1f}" x2="{w-MR}" y2="{Y(t):.1f}" '
                 f'class="gl"/><line x1="{X(t):.1f}" y1="{MT}" x2="{X(t):.1f}" '
                 f'y2="{h-MB}" class="gl"/>'
                 f'<text x="{ML-7}" y="{Y(t)+3:.1f}" text-anchor="end" '
                 f'class="tk">{t:.1f}</text>'
                 f'<text x="{X(t):.1f}" y="{h-MB+15}" '
                 f'text-anchor="{"start" if g==0 else "end" if g==5 else "middle"}" '
                 f'class="tk">{t:.1f}</text>')
    o.append(f'<line x1="{X(0):.1f}" y1="{Y(0):.1f}" x2="{X(1):.1f}" '
             f'y2="{Y(1):.1f}" style="stroke:var(--fg);stroke-width:1.6"/>')
    for dd, dash in ((0.05, "5 4"), (0.10, "2 5")):
        for s in (+1, -1):
            a, b = max(0.0, -s*dd), min(1.0, 1.0 - s*dd)
            o.append(f'<line x1="{X(a):.1f}" y1="{Y(a+s*dd):.1f}" '
                     f'x2="{X(b):.1f}" y2="{Y(b+s*dd):.1f}" '
                     f'style="stroke:var(--mut);stroke-width:1;'
                     f'stroke-dasharray:{dash}"/>')
    o.append(f'<line x1="{X(lim):.1f}" y1="{MT}" x2="{X(lim):.1f}" y2="{h-MB}" '
             f'style="stroke:var(--warn);stroke-width:1.3"/>'
             f'<line x1="{ML}" y1="{Y(lim):.1f}" x2="{w-MR}" y2="{Y(lim):.1f}" '
             f'style="stroke:var(--warn);stroke-width:1.3"/>')
    for ob, pr, cid, src in pts:
        perigo = ob < lim <= pr
        cor = "var(--warn)" if perigo else "var(--accent)"
        o.append(f'<circle cx="{X(ob):.1f}" cy="{Y(pr):.1f}" '
                 f'r="{4.6 if perigo else 3.0}" style="fill:{cor};'
                 f'fill-opacity:{0.95 if perigo else 0.55}">'
                 f'<title>{_esc.escape(cid)} ({_esc.escape(src)}) — '
                 f'dado {ob:.3f} · modelo {pr:.3f}'
                 f'{" — FALSO SEGURO" if perigo else ""}</title></circle>')
    o.append(f'<text x="{X(lim/2):.0f}" y="{Y(0.97):.0f}" text-anchor="middle" '
             f'class="tk" style="fill:var(--warn)">falso SEGURO — o modelo diz '
             f'que retém, o ensaio diz que afrouxou</text>')
    o.append(f'<text x="{(ML+w-MR)/2:.0f}" y="{h-6}" text-anchor="middle" '
             f'class="tk">retenção OBSERVADA (fim do ensaio)</text>'
             f'<text x="13" y="{(MT+h-MB)/2:.0f}" class="tk" text-anchor="middle" '
             f'transform="rotate(-90 13 {(MT+h-MB)/2:.0f})">retenção PREVISTA</text>')
    return (f'<svg viewBox="0 0 {w} {h}" role="img" '
            f'aria-label="paridade previsto contra observado">{"".join(o)}</svg>')


def _svg_cobertura(pts, xlab, ylab, w=860, h=340, logx=False, logy=False):
    """Onde há dado no espaço de condições — e onde não há."""
    if not pts:
        return ""
    import math
    ML, MR, MT, MB = 62, 18, 14, 46
    fx = (lambda v: math.log10(max(v, 1e-9))) if logx else (lambda v: v)
    fy = (lambda v: math.log10(max(v, 1e-9))) if logy else (lambda v: v)
    xs = [fx(p[0]) for p in pts]
    ys = [fy(p[1]) for p in pts]
    x0, x1 = min(xs), max(xs)
    y0, y1 = min(ys), max(ys)
    if x1 - x0 < 1e-9:
        x1 = x0 + 1
    if y1 - y0 < 1e-9:
        y1 = y0 + 1
    X = lambda v: ML + (fx(v) - x0) / (x1 - x0) * (w - ML - MR)
    Y = lambda v: MT + (1 - (fy(v) - y0) / (y1 - y0)) * (h - MT - MB)
    o = []
    for g in range(5):
        tx = x0 + (x1 - x0) * g / 4
        ty = y0 + (y1 - y0) * g / 4
        rx = f"{10**tx:.3g}" if logx else f"{tx:.3g}"
        ry = f"{10**ty:.3g}" if logy else f"{ty:.3g}"
        yy = MT + (1 - g / 4) * (h - MT - MB)
        xx = ML + g / 4 * (w - ML - MR)
        o.append(f'<line x1="{ML}" y1="{yy:.1f}" x2="{w-MR}" y2="{yy:.1f}" '
                 f'class="gl"/><line x1="{xx:.1f}" y1="{MT}" x2="{xx:.1f}" '
                 f'y2="{h-MB}" class="gl"/>'
                 f'<text x="{ML-7}" y="{yy+3:.1f}" text-anchor="end" class="tk">'
                 f'{ry}</text>'
                 f'<text x="{xx:.1f}" y="{h-MB+15}" '
                 f'text-anchor="{"start" if g==0 else "end" if g==4 else "middle"}" '
                 f'class="tk">{rx}</text>')
    for vx, vy, cid, ok in pts:
        o.append(f'<circle cx="{X(vx):.1f}" cy="{Y(vy):.1f}" r="3.4" '
                 f'style="fill:{"var(--accent)" if ok else "var(--warn)"};'
                 f'fill-opacity:.6"><title>{_esc.escape(cid)} — '
                 f'{xlab} {vx:.4g} · {ylab} {vy:.4g}'
                 f'{"" if ok else " (fora do tripé)"}</title></circle>')
    o.append(f'<text x="{(ML+w-MR)/2:.0f}" y="{h-6}" text-anchor="middle" '
             f'class="tk">{_esc.escape(xlab)}</text>'
             f'<text x="13" y="{(MT+h-MB)/2:.0f}" class="tk" text-anchor="middle" '
             f'transform="rotate(-90 13 {(MT+h-MB)/2:.0f})">'
             f'{_esc.escape(ylab)}</text>')
    return (f'<svg viewBox="0 0 {w} {h}" role="img" '
            f'aria-label="cobertura em {_esc.escape(xlab)} e {_esc.escape(ylab)}">'
            f'{"".join(o)}</svg>')


def pagina_qualificacao(comp, res, pisos) -> str:
    """Os 3 eixos de QUALIFICACAO que a validacao por curva nao cobre."""
    cens = [r for r in comp if rh.caso_comparavel(r.source, r.case_id)]
    P = []
    for r in cens:
        rr = res.get(r.case_id)
        if rr is None or not (rr.metric_data and rr.metric_pred):
            continue
        P.append((float(rr.metric_data[-1]), float(rr.metric_pred[-1]),
                  r.case_id, r.source,
                  bool(rh._tripe_ok(rr, rh.limite_sres(r.source, pisos)))))
    O = np.array([p[0] for p in P])
    M = np.array([p[1] for p in P])
    b = M - O
    r2 = 1 - float(np.sum(b**2) / np.sum((O - O.mean())**2))

    # --- 1. decisao ------------------------------------------------------
    blocos = []
    tabs = []
    for lim, norma in ((0.85, "ISO 16130"), (0.80, "DIN 25201-4")):
        vp = int(np.sum((O < lim) & (M < lim)))
        vn = int(np.sum((O >= lim) & (M >= lim)))
        fa = int(np.sum((O >= lim) & (M < lim)))
        fs = int(np.sum((O < lim) & (M >= lim)))
        tabs.append((norma, lim, (vp + vn) / len(O), fa, fs, vp, vn))
    fs_list = sorted([p for p in P if p[0] < 0.85 <= p[1]], key=lambda q: q[1] - q[0],
                     reverse=True)
    fs_tri = [p for p in fs_list if p[4]]
    linhas_fs = "".join(
        f'<tr><td><code>{_esc.escape(c)}</code></td>'
        f'<td class="n">{o:.3f}</td><td class="n">{m:.3f}</td>'
        f'<td class="n">{m-o:+.3f}</td>'
        f'<td>{"<b>SIM</b>" if t else "não"}</td>'
        f'<td><a href="artigo_{_esc.escape(s)}.html">{_esc.escape(s)}</a></td></tr>'
        for o, m, c, s, t in fs_list)
    tab_dec = "".join(
        f'<tr><td>{n}</td><td class="n">{l:.0%}</td><td class="n">{a:.1%}</td>'
        f'<td class="n">{fa}</td><td class="n"><b>{fs}</b></td></tr>'
        for n, l, a, fa, fs, _vp, _vn in tabs)

    # --- 3. cobertura ----------------------------------------------------
    cov1, cov2 = [], []
    for r in cens:
        rr = res.get(r.case_id)
        if rr is None:
            continue
        vc = r.validation_case
        ok = bool(rh._tripe_ok(rr, rh.limite_sres(r.source, pisos)))
        amp = float(getattr(vc, "transverse_displacement_mm", 0) or 0)
        f0 = float(getattr(vc, "initial_preload_N", 0) or 0) / 1000.0
        d = float(getattr(vc, "bolt_diameter_mm", 0) or 0)
        fr = float(getattr(vc, "frequency_Hz", 0) or 0)
        if amp > 0 and f0 > 0:
            cov1.append((amp, f0, r.case_id, ok))
        if d > 0 and fr > 0:
            cov2.append((d, fr, r.case_id, ok))

    corpo = f"""
<h1>Qualificação do software</h1>
<p class="sub">Os eixos que a validação por curva <b>não</b> cobre: aptidão para
a decisão, acurácia global e envelope de validade. <b>{len(P)}</b> curvas
comparáveis.</p>
<p class="nav"><a href="index.html">&larr; metodologia</a></p>

<h2>1. A decisão de engenharia</h2>
<table><tr><th>norma</th><th>limiar</th><th>acerto</th>
<th>falso alarme</th><th>falso SEGURO</th></tr>{tab_dec}</table>
{expl('a classificação que o software de fato entrega ao usuário: a junta '
      '<b>retém</b> acima do limiar da norma, ou não?',
      '<b>falso alarme</b> (diz que afrouxa e não afrouxou) custa dinheiro; '
      '<b>falso seguro</b> (diz que retém e afrouxou) custa a junta. Os dois '
      'erros não são simétricos, e só um deles é perigoso.',
      f'com {len(P)} curvas: acerto de <b>{tabs[0][2]:.1%}</b> na ISO 16130 e '
      f'<b>{tabs[1][2]:.1%}</b> na DIN 25201-4, com <b>{tabs[0][4]}</b> e '
      f'<b>{tabs[1][4]}</b> falsos seguros.')}

<h3>Os falsos seguros, nomeados</h3>
<table><tr><th>curva</th><th>dado</th><th>modelo</th><th>Δ</th>
<th>passa o tripé?</th><th>artigo</th></tr>{linhas_fs}</table>
{expl('as curvas do quadrante perigoso, no limiar da ISO 16130.',
      '⚠️ <b>{n} delas PASSAM o tripé.</b> A primeira tem MAE excelente e mesmo '
      'assim informaria retenção acima do limiar onde o ensaio mede abaixo. '
      '<b>O tripé mede fidelidade de curva; ele não mede acerto de decisão</b> — '
      'e os dois podem discordar. Não é defeito do tripé: é uma pergunta que ele '
      'não faz.'.format(n=len(fs_tri)),
      f'<b>{len(fs_tri)}</b> de <b>{len(fs_list)}</b> falsos seguros estão '
      f'aprovados pela régua vigente.', aviso=True)}

<h2>2. Paridade: previsto × observado</h2>
{_svg_paridade([(p[0], p[1], p[2], p[3]) for p in P])}
{expl('cada ponto é uma curva, no seu ponto final. A reta cheia é 1:1; as '
      'tracejadas são ±0,05 e ±0,10; a faixa âmbar é o quadrante de falso '
      'seguro.',
      'ponto <b>acima</b> da reta = o modelo retém mais que o ensaio. Um viés '
      'sistemático para cima é exatamente o que produz falso seguro, e é por '
      'isso que este gráfico e a tabela acima são o mesmo fato visto de dois '
      'ângulos.',
      f'R² contra a reta 1:1 = <b>{r2:.4f}</b>; viés médio '
      f'<b>{b.mean():+.4f}</b> (positivo ⇒ o modelo retém mais); '
      f'<b>{100*np.mean(np.abs(b)<=0.05):.0f} %</b> dentro de ±0,05 e '
      f'<b>{100*np.mean(np.abs(b)<=0.10):.0f} %</b> dentro de ±0,10.')}

<h2>3. Envelope de validade</h2>
{_svg_cobertura(cov1, "amplitude transversal [mm]", "F₀ [kN]", logx=True, logy=True)}
{_svg_cobertura(cov2, "diâmetro [mm]", "frequência [Hz]", logy=True)}
{expl('um ponto por curva no espaço de condições; <b>âmbar</b> = fora do tripé.',
      'o que se lê aqui é <b>onde o software foi validado</b>. Uma junta que caia '
      'num vazio do gráfico está fora do envelope — o modelo vai devolver um '
      'número, e ninguém mediu se ele vale ali. É o que transforma "validado em '
      '205 curvas" em "validado NESTE envelope".',
      f'amplitude <b>{min(p[0] for p in cov1):.2f}–{max(p[0] for p in cov1):.2f} mm</b> · '
      f'F₀ <b>{min(p[1] for p in cov1):.1f}–{max(p[1] for p in cov1):.0f} kN</b> · '
      f'diâmetro <b>{min(p[0] for p in cov2):.0f}–{max(p[0] for p in cov2):.0f} mm</b> · '
      f'frequência <b>{min(p[1] for p in cov2):.2g}–{max(p[1] for p in cov2):.0f} Hz</b>.')}

<h2>O que ainda falta para qualificar</h2>
{expl('estes três eixos cobrem <b>aptidão para a decisão</b>, <b>acurácia '
      'global</b> e <b>envelope</b>.',
      'falta o outro lado da qualificação — a <b>verificação</b>: o residual de '
      'conservação de energia por caso (o engine calcula, o store <b>não '
      'grava</b>), a independência de passo de integração, e um held-out '
      'sistemático que separe predição de ajuste com número.',
      'a lista completa, com custo declarado por item, está em '
      '<code>New_Theory/qualificacao_o_que_falta.md</code>.', aviso=True)}
"""
    return pagina("Qualificação do software", corpo)


def main():
    comp, res, pisos = carrega()
    store = json.loads((RAIZ / "Models" / "CALIBRATION_AND_VALIDATION"
                        / "validation_store.json").read_text(encoding="utf-8"))
    SAIDA.mkdir(parents=True, exist_ok=True)
    fams = familias(comp, res)
    com_repl = {k[0] for k in fams}
    fontes = sorted({r.source for r in comp})
    for f in fontes:
        (SAIDA / f"artigo_{f}.html").write_text(
            pagina_artigo(f, comp, res, pisos, store, f in com_repl),
            encoding="utf-8", newline="")
    print(f"{len(fontes)} paginas por artigo")
    for nome, gerador in (("global_tipos.html",
                           lambda: pagina_tipos(comp, res, pisos, store)),
                          ("global_parametros.html", pagina_parametros),
                          ("fluxo.html", lambda: pagina_fluxo(comp, res, pisos)),
                          ("qualificacao.html", lambda: pagina_qualificacao(comp, res, pisos)),
                          ("modelo_nao_fit.html",
                           lambda: pagina_modelo_nao_fit(comp, res, pisos))):
        html = gerador()
        if html:
            (SAIDA / nome).write_text(html, encoding="utf-8", newline="")
            print(f"  {nome}")
    # indice: acrescenta os links na pagina de metodologia
    idx_p = SAIDA / "index.html"
    idx = idx_p.read_text(encoding="utf-8")
    marca = '<h2>11. Por artigo</h2>'
    if marca in idx:
        idx = idx[:idx.index(marca)] + "</div></body></html>"
    links = "".join(
        f'<li><a href="artigo_{f}.html">{_esc.escape(f)}</a></li>'
        for f in fontes)
    bloco = (f'<h2>11. Por artigo</h2>'
             f'<p>Uma página por fonte: todas as curvas, o erro por perna em '
             f'múltiplos do limite, a decomposição por mecanismo e as constantes '
             f'com procedência.</p><ul>{links}</ul>'
             f'<h2>12. Visões globais</h2><ul>'
             f'<li><a href="global_tipos.html">Comportamento médio por tipo de '
             f'curva</a> — axial × transversal, diâmetro, atrito, mecanismo</li>'
             f'<li><a href="global_parametros.html">Efeito dos parâmetros</a> — '
             f'sensibilidade OAT por família, e os congelados</li>'
             f'<li><a href="modelo_nao_fit.html">É modelo, não fit</a> — mesmas '
             f'constantes, comportamentos opostos</li>'
             f'<li><a href="qualificacao.html"><b>Qualificação do software</b></a> — '
             f'decisão de engenharia, paridade e envelope de validade</li>'
             f'<li><a href="fluxo.html">Fluxo de uso do projeto</a> — do PDF à '
             f'adoção</li></ul>')
    idx = idx.replace("</div></body>", bloco + "</div></body>")
    idx_p.write_text(idx, encoding="utf-8", newline="")
    print(f"\nindice atualizado; total em {SAIDA}")


if __name__ == "__main__":
    main()
