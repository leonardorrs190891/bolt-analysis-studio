# -*- coding: utf-8 -*-
"""Gera `New_Theory/metodologia/` — a cadeia de extracao de curvas, com plots.

Duas entregas, pedidas pelo professor em 2026-08-25:

1. **`index.html`** — a metodologia COMPLETA, etapa por etapa, sobre uma curva de
   referencia escolhida por MEDICAO (nao por gosto): `liu2016wear_fig11a_af7p5kn`,
   MAE **0,0121**, o melhor fit da fonte `LIU_2016`, que fecha **14/14** no tripe
   e tem a figura do artigo disponivel. Onde uma etapa e INERTE nessa curva, a
   pagina mostra outra curva onde ela AGE — dizer "esta etapa existe" sem
   mostra-la agindo seria pior que omiti-la.

2. **`replicas_<FONTE>.html`** — uma por fonte com replica: a previsao do modelo
   contra TODAS as replicas, e o erro contra cada uma.

Sem dependencia externa: SVG puro, PNG embutido como data URI (a pagina abre em
`file://`). Todos os numeros sao RECOMPUTADOS aqui — nenhum literal em prosa.

    py -3.12 New_Theory/build_metodologia.py
"""
from __future__ import annotations

import base64
import collections
import html as _esc
import itertools
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

import numpy as np  # noqa: E402

import bolt_analysis_studio.validation.report_html as rh  # noqa: E402
import bolt_analysis_studio.validation.runner as rn  # noqa: E402
from bolt_analysis_studio.validation.case_registry import all_records  # noqa: E402
from bolt_analysis_studio.validation.inputs import load_full_curve  # noqa: E402
from bolt_analysis_studio.validation.runner import CaseResult  # noqa: E402

REF = "liu2016wear_fig11a_af7p5kn"
REF_FIG = "liu_2016__fig11.png"
EX_TRIM = "liu2016wear_fig7_run2_5e6cyc"      # onde `trim_n_max` AGE
EX_ESCALA = "eccles2010_fig8a_no_axial_baseline1"   # onde `csv_x_scale` AGE
SAIDA = RAIZ / "New_Theory" / "metodologia"

CSS = """
:root{--bg:#0f1115;--fg:#e6e8ec;--mut:#9aa3af;--accent:#5aa9e6;--warn:#e6a15a;
--ok:#5ae6a9;--line:#2a2f3a;--card:#161a21}
@media(prefers-color-scheme:light){:root{--bg:#fbfcfd;--fg:#1a1d23;--mut:#5b6472;
--accent:#1f6fb2;--warn:#a8620f;--ok:#127a52;--line:#dfe3ea;--card:#fff}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);
font:15px/1.62 -apple-system,Segoe UI,Roboto,sans-serif}
.wrap{max-width:900px;margin:0 auto;padding:28px 20px 80px}
h1{font-size:1.6rem;margin:.2em 0 .1em}h2{font-size:1.15rem;margin:2.2em 0 .4em;
padding-top:.6em;border-top:1px solid var(--line)}h3{font-size:1rem;margin:1.4em 0 .3em}
p{margin:.5em 0}code{font-family:Consolas,monospace;color:var(--accent);font-size:.92em}
.sub{color:var(--mut);font-size:.9rem}
.card{background:var(--card);border:1px solid var(--line);border-radius:9px;
padding:12px 14px;margin:.8em 0}
.expl{background:var(--card);border-left:3px solid var(--accent);border-radius:0 7px 7px 0;
padding:9px 13px;margin:.7em 0;font-size:.9rem}
.expl .q{color:var(--accent);font-weight:600}
.av{border-left-color:var(--warn)}.av .q{color:var(--warn)}
table{border-collapse:collapse;width:100%;margin:.7em 0;font-size:.88rem}
th,td{border-bottom:1px solid var(--line);padding:5px 8px;text-align:left}
th{color:var(--mut);font-weight:600}td.n{text-align:right;font-variant-numeric:tabular-nums}
svg{width:100%;height:auto;display:block;margin:.5em 0}
.gl{stroke:var(--line);stroke-width:1}.ax{stroke:var(--mut);stroke-width:1}
.tk{fill:var(--mut);font-size:10px;font-family:Consolas,monospace}
img{max-width:100%;height:auto;border-radius:7px;border:1px solid var(--line)}
a{color:var(--accent)}.nav{font-size:.9rem;margin:.6em 0}
ul{margin:.4em 0 .4em 1.1em;padding:0}li{margin:.2em 0}
"""


# --------------------------------------------------------------------------- #
# Plot: um helper so, com eixos rotulados                                     #
# --------------------------------------------------------------------------- #

def plot(series, xlab, ylab, w=860, h=330, logx=False, ylim=None, hlines=()):
    """`series` = [(xs, ys, rotulo, cor, modo)] · modo em {'linha','ponto','ambos'}.

    ⚠️ Rotulo do ultimo tick ancora em `end` e o do primeiro em `start`: com
    `middle` eles vazam o viewBox, e SVG corta texto fora EM SILENCIO — defeito
    medido em 2026-08-25 no report (`BAUER24` terminava em 587 num viewBox 560).
    """
    ML, MR, MT, MB = 62, 18, 14, 46
    xs_all = [x for s in series for x in s[0] if (not logx or x > 0)]
    ys_all = [y for s in series for y in s[1]]
    if not xs_all or not ys_all:
        return ""
    f = (lambda v: np.log10(max(v, 1e-9))) if logx else (lambda v: v)
    x0, x1 = f(min(xs_all)), f(max(xs_all))
    if x1 - x0 < 1e-12:
        x1 = x0 + 1.0
    y0, y1 = (ylim if ylim else (min(0.0, min(ys_all)), max(ys_all) * 1.06))
    if y1 - y0 < 1e-12:
        y1 = y0 + 1.0
    X = lambda v: ML + (f(v) - x0) / (x1 - x0) * (w - ML - MR)
    Y = lambda v: MT + (1 - (v - y0) / (y1 - y0)) * (h - MT - MB)
    o = []
    for g in range(5):
        ty = y0 + (y1 - y0) * g / 4
        tx = x0 + (x1 - x0) * g / 4
        rot = f"{10 ** tx:.3g}" if logx else f"{tx:.4g}"
        anc = "start" if g == 0 else ("end" if g == 4 else "middle")
        o.append(f'<line x1="{ML}" y1="{Y(ty):.1f}" x2="{w-MR}" y2="{Y(ty):.1f}" '
                 f'class="gl"/>'
                 f'<text x="{ML-7}" y="{Y(ty)+3:.1f}" text-anchor="end" class="tk">'
                 f'{ty:.4g}</text>'
                 f'<text x="{X(10**tx if logx else tx):.1f}" y="{h-MB+15}" '
                 f'text-anchor="{anc}" class="tk">{rot}</text>')
    for yv, cor, rot in hlines:
        if y0 <= yv <= y1:
            o.append(f'<line x1="{ML}" y1="{Y(yv):.1f}" x2="{w-MR}" y2="{Y(yv):.1f}" '
                     f'style="stroke:{cor};stroke-width:1;stroke-dasharray:5 4"/>'
                     f'<text x="{w-MR-3}" y="{Y(yv)-4:.1f}" text-anchor="end" '
                     f'class="tk" style="fill:{cor}">{_esc.escape(rot)}</text>')
    leg = []
    for i, (xs, ys, rot, cor, modo) in enumerate(series):
        pts = [(X(x), Y(y)) for x, y in zip(xs, ys) if (not logx or x > 0)]
        if not pts:
            continue
        if modo in ("linha", "ambos"):
            d = " ".join(f"{'M' if k == 0 else 'L'}{px:.1f} {py:.1f}"
                         for k, (px, py) in enumerate(pts))
            o.append(f'<path d="{d}" fill="none" style="stroke:{cor};'
                     f'stroke-width:{2.0 if modo == "linha" else 1.4}"/>')
        if modo in ("ponto", "ambos"):
            for px, py in pts:
                o.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3.1" '
                         f'style="fill:{cor};fill-opacity:.9"/>')
        # ⚠️ Rotulo VAZIO nao entra na legenda: as series de modelo reusam a cor
        # do dado e sao nomeadas por ele. Antes elas avancavam `lx` do mesmo
        # jeito, gastando o dobro do espaco e deixando retangulos sem texto fora
        # do viewBox (medido: 153 textos vazando nas paginas por artigo).
        if rot:
            leg.append((rot, cor))
    # ⚠️ E a legenda QUEBRA em linhas: com 9 curvas ela passa de 860 mesmo sem
    # os rotulos vazios. SVG corta fora do viewBox em silencio.
    lx, ly, nlin = ML + 6, MT + 3, 1
    for rot, cor in leg:
        larg_it = 20 + len(rot) * 5.6
        if lx + larg_it > w - MR and lx > ML + 6:
            lx, ly, nlin = ML + 6, ly + 13, nlin + 1
        o.append(f'<rect x="{lx}" y="{ly}" width="9" height="9" rx="2" '
                 f'style="fill:{cor}"/>'
                 f'<text x="{lx+13}" y="{ly+8.5}" class="tk">'
                 f'{_esc.escape(rot)}</text>')
        lx += larg_it
    o.append(f'<text x="{(ML+w-MR)/2:.0f}" y="{h-6}" text-anchor="middle" '
             f'class="tk">{_esc.escape(xlab)}</text>'
             f'<text x="13" y="{(MT+h-MB)/2:.0f}" class="tk" text-anchor="middle" '
             f'transform="rotate(-90 13 {(MT+h-MB)/2:.0f})">{_esc.escape(ylab)}</text>')
    # cada linha extra de legenda empurra o topo: cresce o viewBox em vez de
    # deixar a legenda por cima da curva.
    extra = (nlin - 1) * 13
    return (f'<svg viewBox="0 {-extra} {w} {h + extra}" role="img" '
            f'aria-label="{_esc.escape(ylab)} contra {_esc.escape(xlab)}">'
            f'{"".join(o)}</svg>')


def expl(variaveis, como, leitura, aviso=False):
    c = "expl av" if aviso else "expl"
    return (f'<div class="{c}"><p><span class="q">As variáveis:</span> {variaveis}</p>'
            f'<p><span class="q">Como ler:</span> {como}</p>'
            f'<p><span class="q">Leitura do dado atual:</span> {leitura}</p></div>')


def pagina(titulo, corpo, nav=""):
    return (f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{_esc.escape(titulo)}</title><style>{CSS}</style></head><body>'
            f'<div class="wrap">{nav}{corpo}</div></body></html>')


# --------------------------------------------------------------------------- #

def carrega():
    store = json.loads((RAIZ / "Models" / "CALIBRATION_AND_VALIDATION"
                        / "validation_store.json").read_text(encoding="utf-8"))
    recs = store.get("cases", store)
    comp = [r for r in all_records()
            if r.case_id in recs and rh.caso_no_documento(r.source, r.case_id)]
    res = {}
    for r in comp:
        try:
            res[r.case_id] = CaseResult.from_dict(recs[r.case_id])
        except Exception:
            pass
    pisos = rh._pisos_medidos([(r.source, res[r.case_id]) for r in comp
                               if r.case_id in res])
    return comp, res, pisos


def cru(rec, vc):
    """CSV como foi digitalizada, e depois com `(x−offset)·scale` aplicado."""
    x, y = load_full_curve(rec.csv_path)
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    off = float(getattr(vc, "csv_x_offset", 0) or 0)
    sc = float(getattr(vc, "csv_x_scale", 1) or 1)
    return x, y, np.clip((x - off) * sc, 0, None), off, sc


def familias(comp, res):
    vcs = {r.case_id: r.validation_case for r in comp}
    gr = collections.defaultdict(list)
    for r in comp:
        rr = res.get(r.case_id)
        if rr is None or not getattr(rr, "metric_x", None):
            continue
        if (r.case_id in rh._SEM_FAMILIA_MECANICA
                and r.source not in rh._FONTES_RESOLVIDAS_POR_CHAVE):
            continue
        cfg = getattr(rr, "config_used", None) or {}
        try:
            k = (r.source, round(float(cfg.get("delta_mm") or 0), 4),
                 round(float(cfg.get("F_amp_N") or 0), 1), cfg.get("mode"))
        except (TypeError, ValueError):
            continue
        vc = vcs.get(r.case_id)
        if vc is not None:
            k = k + tuple(getattr(vc, c, None) for c in rh._CAMPOS_VARRIDOS)
        gr[k].append(r.case_id)
    return {k: v for k, v in gr.items() if len(v) > 1}


# --------------------------------------------------------------------------- #
# Pagina 1 — a cadeia de extracao                                             #
# --------------------------------------------------------------------------- #

def metodologia(comp, res, pisos) -> str:
    porid = {r.case_id: r for r in comp}
    rec = porid[REF]
    vc = rec.validation_case
    r = res[REF]
    x_cru, y_cru, x_conv, off, sc = cru(rec, vc)
    mx = np.asarray(r.metric_x, float)
    md = np.asarray(r.metric_data, float)
    mp = np.asarray(r.metric_pred, float)
    lim_sd = rh.limite_sres(rec.source, pisos)
    sd = rh.sres_para_censo(r)
    resid = mp - md
    trim_ref = rn._trim_n_for(rec.source, REF, "")

    n_ok = sum(1 for c in comp if c.source == rec.source
               and rh._tripe_ok(res.get(c.case_id), rh.limite_sres(c.source, pisos)))
    n_tot = sum(1 for c in comp if c.source == rec.source)

    fig = SAIDA.parent / "variable_explorer" / "paper_figures" / REF_FIG
    img = ""
    if fig.exists():
        b64 = base64.b64encode(fig.read_bytes()).decode()
        img = (f'<img src="data:image/png;base64,{b64}" '
               f'alt="figura do artigo, fonte {_esc.escape(rec.source)}">')

    # --- etapa da escala: onde ela AGE -----------------------------------
    rec_e = porid.get(EX_ESCALA)
    esc_txt = ""
    if rec_e is not None:
        xe, ye, xe2, offe, sce = cru(rec_e, rec_e.validation_case)
        esc_txt = (
            f'<p>Nesta curva a etapa é <b>inerte</b> (<code>offset</code>=0, '
            f'<code>scale</code>=1) — mas ela não é decorativa. Na '
            f'<code>{_esc.escape(EX_ESCALA)}</code> o eixo do artigo está em '
            f'<b>segundos</b> e <code>csv_x_scale={sce:g}</code> o converte em '
            f'ciclos: o último ponto vai de <b>{xe.max():.0f}</b> para '
            f'<b>{xe2.max():.0f}</b>. Em curvas do <code>LU_2024</code> e do '
            f'<code>KARLSEN_2022</code> o <code>offset</code>=1 remove a âncora '
            f'pré-ciclagem que o artigo plota em x=1 por causa do eixo log.</p>')

    # --- etapa do trim: onde ela AGE -------------------------------------
    rec_t = porid.get(EX_TRIM)
    trim_html = ""
    if rec_t is not None:
        rt = res[EX_TRIM]
        xt, yt, xt2, _o, _s = cru(rec_t, rec_t.validation_case)
        mtx = np.asarray(rt.metric_x, float)
        corta = [(a, b) for a, b in zip(xt2, yt) if a > mtx.max() + 1e-9]
        tn = rn._trim_n_for(rec_t.source, EX_TRIM, "")
        trim_html = (
            f'<h3>Onde o trim age: <code>{_esc.escape(EX_TRIM)}</code></h3>'
            + plot([(xt2, yt, "CSV crua", "var(--mut)", "ambos"),
                    (mtx, np.asarray(rt.metric_data, float),
                     "dentro da janela", "var(--accent)", "ambos")],
                   "ciclo", "F/F₀",
                   hlines=[(0.10, "var(--warn)", "FLOOR_TRIM 0,10")])
            + expl(
                'a mesma curva com os pontos que a métrica <b>pontua</b> '
                'destacados. A linha tracejada é o <code>FLOOR_TRIM</code>=0,10.',
                f'os pontos cinza à direita existem no dado e <b>não entram no '
                f'erro</b>: <code>cfg.trim_n_max</code>={tn:.3g} fecha a janela '
                f'ali. &#9888; O trim não só filtra a métrica — ele <b>encurta a '
                f'simulação</b>, então o modelo nem chega a ser calculado depois '
                f'desse ponto.',
                f'<b>{len(xt2)}</b> pontos digitalizados, <b>{len(mtx)}</b> '
                f'pontuados, <b>{len(corta)}</b> fora da janela.', aviso=True))

    pernas = [("MAE", float(np.abs(resid).mean()), rh.META_MAE),
              ("resíduo máximo", float(np.abs(resid).max()), rh.META_MAX),
              ("σ_res", float(sd), lim_sd)]
    linhas = "".join(
        f'<tr><td>{n}</td><td class="n">{v:.4f}</td><td class="n">{l:.4f}</td>'
        f'<td class="n">{v / l:.2f}x</td>'
        f'<td>{"passa" if v <= l else "reprova"}</td></tr>'
        for n, v, l in pernas)

    fams = familias(comp, res)
    piso_html = ""
    # ⚠️ A curva de referência NÃO tem irmã de réplica — a família com réplica
    # do LIU_2016 é o par  × . Sem este fallback a etapa do
    # piso saía VAZIA e a página pulava de 7 para 9 em silêncio, o que é pior que
    # omitir: o leitor não tem como saber que faltou.
    irmas = next((v for v in fams.values() if REF in v), None)
    _da_ref = irmas is not None
    if irmas is None:
        irmas = next((v for k, v in fams.items() if k[0] == rec.source), None)
    if irmas and len(irmas) > 1:
        ss = [(np.asarray(res[c].metric_x, float),
               np.asarray(res[c].metric_data, float), c) for c in irmas]
        lo = max(s[0].min() for s in ss)
        hi = min(s[0].max() for s in ss)
        g = np.linspace(lo, hi, 60)
        Z = {c: np.interp(g, xx, yy) for xx, yy, c in ss}
        banda = max(np.abs(Z[a] - Z[b]).max()
                    for a, b in itertools.combinations(Z, 2))
        cores = ("var(--accent)", "var(--warn)", "var(--ok)", "var(--mut)")
        nota_ref = ('' if _da_ref else
                    f'<p class="sub">⚠️ A curva de referência não tem réplica; '
                    f'estas são as da mesma fonte '
                    f'(<code>{_esc.escape(rec.source)}</code>) que têm — a etapa '
                    f'existe e é mostrada <b>agindo</b>, como as §3 e §5.</p>')
        piso_html = (
            '<h2>8. O piso: o que o próprio dado não distingue</h2>' + nota_ref
            + plot([(xx, yy, c.split("_")[-1], cores[i % 4], "ambos")
                    for i, (xx, yy, c) in enumerate(ss)], "ciclo", "F/F₀")
            + expl(
                'as réplicas da mesma condição, cada uma com sua cor.',
                'a distância <b>entre elas</b> é o que o experimento não repete '
                '— e é o denominador contra o qual o erro do modelo tem de ser '
                'lido. Cobrar do modelo precisão maior que essa é cobrar que ele '
                'acerte melhor do que o ensaio se repete.',
                f'banda medida na janela comum: <b>{banda:.4f}</b>; o limite de '
                f'σ_res desta fonte é <code>max(0,025; piso)</code> = '
                f'<b>{lim_sd:.4f}</b>.'))

    p1 = plot([(x_cru, y_cru, "CSV crua", "var(--accent)", "ambos")],
              "x da CSV", "F/F₀")
    p2 = plot([(mx, md, "dado", "var(--accent)", "ambos"),
               (mx, mp, "modelo", "var(--warn)", "linha")], "ciclo", "F/F₀")
    p3 = plot([(mx, md, "dado pontuado", "var(--accent)", "ambos")], "ciclo",
              "F/F₀", hlines=[(0.10, "var(--warn)", "FLOOR_TRIM 0,10")])
    p4 = plot([(mx, resid, "resíduo (modelo − dado)", "var(--accent)", "ambos")],
              "ciclo", "resíduo",
              hlines=[(0.0, "var(--mut)", "zero"),
                      (float(np.abs(resid).max()), "var(--warn)", "res.máx")])
    trim_txt = "—" if trim_ref is None else f"{trim_ref:.3g}"
    align = float(getattr(r, "align", 1) or 1)

    corpo = f"""
<h1>Metodologia de extração de curvas</h1>
<p class="sub">Da figura do artigo até as três pernas do tripé, etapa por etapa,
sobre uma curva de referência. Gerado por
<code>New_Theory/build_metodologia.py</code>; todos os números são recomputados
do store canônico.</p>

<div class="card"><p><b>Curva de referência:
<code>{_esc.escape(REF)}</code></b> — escolhida por MEDIÇÃO, não por gosto: é o
melhor fit da fonte <code>{_esc.escape(rec.source)}</code>, que fecha
<b>{n_ok}/{n_tot}</b> no tripé, e é uma das que têm a figura do artigo
disponível. MAE <b>{r.mae:.4f}</b>, res.máx <b>{r.maxerr:.4f}</b>,
σ_res <b>{sd:.4f}</b>.</p>
<p class="sub">Onde uma etapa é <b>inerte</b> nesta curva, a página mostra outra
onde ela <b>age</b> — dizer "esta etapa existe" sem mostrá-la agindo seria pior
que omiti-la.</p></div>

<h2>1. A figura do artigo</h2>
{img}
{expl('o recorte do PDF, como publicado pelos autores.',
      'é o <b>instrumento da conferência</b>: qualquer dúvida sobre a '
      'digitalização se resolve voltando aqui. Por isso a figura é embutida como '
      'PNG sem perda — comprimir com perda o artefato que serve para verificar a '
      'digitalização trocaria a coisa medida pela medição.',
      f'fonte <code>{_esc.escape(rec.source)}</code>, arquivo '
      f'<code>{_esc.escape(REF_FIG)}</code>.')}

<h2>2. Digitalização &rarr; CSV</h2>
{p1}
{expl('os pares (x, y) lidos da figura, exatamente como estão no arquivo.',
      'cada ponto é uma leitura manual sobre o traço publicado. A densidade não '
      'é uniforme de propósito — quem digitaliza põe mais pontos onde a curva '
      'muda de inclinação.',
      f'<b>{len(x_cru)}</b> pontos, x de <b>{x_cru.min():.0f}</b> a '
      f'<b>{x_cru.max():.0f}</b>, y de <b>{y_cru.min():.4f}</b> a '
      f'<b>{y_cru.max():.4f}</b>.')}

<h2>3. Convenções de eixo: <code>(x &minus; offset) &middot; scale</code></h2>
{expl('os dois campos do <code>ValidationCase</code> que corrigem o eixo x antes '
      'de qualquer comparação.',
      '<code>csv_x_offset</code> remove uma âncora que o artigo plota fora da '
      'escala; <code>csv_x_scale</code> converte a unidade do eixo em ciclos. '
      'Todo consumidor da CSV crua tem de aplicar os dois — ler o arquivo sem '
      'eles compara ciclos com segundos.',
      f'nesta curva: offset <b>{off:g}</b>, scale <b>{sc:g}</b>.')}
{esc_txt}

<h2>4. Simulação e alinhamento</h2>
{p2}
{expl('o dado e a previsão do modelo, já na mesma grade.',
      'o modelo é <b>ancorado</b> no primeiro ciclo do dado — dividido pelo '
      'próprio valor ali, de modo que os dois partem de F/F₀=1. O artigo '
      'normaliza naquele ponto, e a queda anterior (assentamento) não tem '
      'contraparte medida para ser cobrada.',
      f'fator de alinhamento aplicado: <b>{align:.4f}</b> '
      f'(1,0 = o modelo já passava pelo ponto).')}

<h2>5. A janela da métrica</h2>
{p3}
{expl('os pontos que de fato entram no erro.',
      'dois filtros agem aqui: <code>FLOOR_TRIM</code>=0,10 tira todo ponto com '
      'F/F₀ abaixo de 0,10, e <code>cfg.trim_n_max</code> fecha a janela num '
      'ciclo declarado. &#9888; Os dois <b>encurtam a simulação junto</b> — não '
      'são só filtro de métrica.',
      f'nesta curva sobram <b>{len(mx)}</b> de <b>{len(x_cru)}</b> pontos; '
      f'<code>trim_n_max</code> = <b>{trim_txt}</b>.')}
{trim_html}

<h2>6. O que a métrica compara</h2>
{expl('os tres vetores que o runner grava: <code>metric_x</code>, '
      '<code>metric_data</code> e <code>metric_pred</code>.',
      '<b>todo consumidor lê daí; ninguém reinterpola.</b> Recomputar a curva '
      'numa grade amostrada dá erro de até 46 % no transiente, e foi assim que a '
      'página chegou a publicar quatro números discordantes para a mesma curva.',
      f'<b>{len(mx)}</b> pontos comparados, de ciclo <b>{mx.min():.0f}</b> a '
      f'<b>{mx.max():.0f}</b>.')}

<h2>7. O resíduo e as três pernas</h2>
{p4}
<table><tr><th>perna</th><th>valor</th><th>limite</th><th>múltiplo</th>
<th>veredito</th></tr>{linhas}</table>
{expl('o resíduo ponto a ponto, e as três normas que o resumem.',
      'as três medem coisas diferentes do <b>mesmo</b> vetor: o MAE é o erro '
      'típico, o res.máx é o pior ponto, e o σ_res é a <b>forma</b> (o quanto '
      'o resíduo oscila em torno do seu próprio viés). Um modelo pode ter MAE '
      'pequeno e σ_res grande — erro pequeno com a forma errada.',
      f'o limite do σ_res é <code>max(0,025; piso da fonte)</code> = '
      f'<b>{lim_sd:.4f}</b> (regra D1), não o global.')}

{piso_html}

<h2>9. Onde cada etapa mora no código</h2>
<table><tr><th>etapa</th><th>arquivo</th><th>símbolo</th></tr>
<tr><td>convenções de eixo</td><td>core/validation_cases.py</td>
<td><code>csv_x_offset</code> &middot; <code>csv_x_scale</code></td></tr>
<tr><td>simulação e alinhamento</td><td>validation/runner.py</td>
<td><code>_simulate_case</code> &middot; <code>CaseResult.align</code></td></tr>
<tr><td>piso da métrica</td><td>validation/runner.py</td>
<td><code>FLOOR_TRIM</code> = 0,10</td></tr>
<tr><td>janela</td><td>validation/runner.py</td>
<td><code>_trim_n_for</code></td></tr>
<tr><td>vetores comparados</td><td>validation/runner.py</td>
<td><code>metric_x</code> &middot; <code>metric_data</code> &middot;
<code>metric_pred</code></td></tr>
<tr><td>as três pernas</td><td>validation/report_html.py</td>
<td><code>_tripe_ok</code> &middot; <code>sres_para_censo</code></td></tr>
<tr><td>limite por fonte</td><td>validation/report_html.py</td>
<td><code>limite_sres</code> &middot; <code>_pisos_medidos</code></td></tr>
</table>
"""
    return pagina("Metodologia de extração de curvas", corpo)


# --------------------------------------------------------------------------- #
# Paginas 2..N — uma por fonte com replica                                    #
# --------------------------------------------------------------------------- #

def pagina_replicas(fonte, conds, res, pisos, comp) -> str:
    """Modelo contra TODAS as replicas da fonte, e o erro contra cada uma."""
    lim_sd = rh.limite_sres(fonte, pisos)
    cores = ("var(--accent)", "var(--warn)", "var(--ok)", "#c86ad0", "#d0a06a",
             "#6ad0c8", "#d06a6a", "#8a9ad0")
    blocos = []
    for idx, cids in enumerate(conds, 1):
        S = [(np.asarray(res[c].metric_x, float),
              np.asarray(res[c].metric_data, float),
              np.asarray(res[c].metric_pred, float), c) for c in cids]
        lo = max(s[0].min() for s in S)
        hi = min(s[0].max() for s in S)
        g = np.linspace(lo, hi, 60)
        D = np.array([np.interp(g, s[0], s[1]) for s in S])
        P = np.array([np.interp(g, s[0], s[2]) for s in S])
        banda = max(np.abs(D[a] - D[b]).max()
                    for a, b in itertools.combinations(range(len(S)), 2))
        r_cond = P.mean(axis=0) - D.mean(axis=0)
        series = [(s[0], s[1], s[3].split("_")[-1][:14], cores[i % len(cores)],
                   "ponto") for i, s in enumerate(S)]
        series.append((g, P.mean(axis=0), "modelo", "#000", "linha"))
        # a curva do modelo em preto some no tema escuro; usa o fg
        series[-1] = (g, P.mean(axis=0), "modelo", "var(--fg)", "linha")
        prev = plot(series, "ciclo", "F/F₀", h=340)

        # erro contra CADA replica, e contra o centro
        linhas = []
        for i, s in enumerate(S):
            e = np.interp(g, s[0], s[2]) - np.interp(g, s[0], s[1])
            linhas.append((s[3], float(np.abs(e).mean()), float(np.abs(e).max()),
                           float(e.std(ddof=1))))
        mae_c = float(np.abs(r_cond).mean())
        mx_c = float(np.abs(r_cond).max())
        sd_c = float(r_cond.std(ddof=1))
        tab = "".join(
            f'<tr><td><code>{_esc.escape(c)}</code></td>'
            f'<td class="n">{a:.4f}</td><td class="n">{b:.4f}</td>'
            f'<td class="n">{d:.4f}</td></tr>' for c, a, b, d in linhas)
        med = float(np.mean([l[1] for l in linhas]))
        razao = med / mae_c if mae_c > 1e-12 else float("inf")
        err = plot([(g, np.interp(g, S[i][0], S[i][2]) - np.interp(g, S[i][0], S[i][1]),
                     S[i][3].split("_")[-1][:14], cores[i % len(cores)], "linha")
                    for i in range(len(S))]
                   + [(g, r_cond, "contra a CONDIÇÃO", "var(--fg)", "linha")],
                   "ciclo", "resíduo", h=300,
                   hlines=[(0.0, "var(--mut)", "zero")])
        blocos.append(
            f'<h2>Condição {idx} — {len(S)} réplicas</h2>{prev}'
            + expl(
                'os pontos são as réplicas do dado, cada uma com sua cor; a linha '
                'grossa é a previsão do modelo.',
                'uma previsão só para várias corridas: o modelo não persegue cada '
                'réplica. A distância entre os pontos de cores diferentes é o que '
                'o experimento <b>não repete</b>.',
                f'banda do dado: <b>{banda:.4f}</b>.')
            + f'<h3>Erro contra cada réplica</h3>{err}'
            + f'<table><tr><th>réplica</th><th>MAE</th><th>res.máx</th>'
              f'<th>σ_res</th></tr>{tab}'
              f'<tr><td><b>contra a CONDIÇÃO</b> (centro)</td>'
              f'<td class="n"><b>{mae_c:.4f}</b></td>'
              f'<td class="n"><b>{mx_c:.4f}</b></td>'
              f'<td class="n"><b>{sd_c:.4f}</b></td></tr></table>'
            + expl(
                'o resíduo do modelo contra cada réplica, e contra o centro delas.',
                'o erro contra uma réplica cobra do modelo o <b>espalhamento</b> '
                'daquela corrida; o erro contra a condição, não. A diferença entre '
                'as duas leituras é o que a réplica adiciona.',
                f'MAE médio contra réplica <b>{med:.4f}</b> contra <b>{mae_c:.4f}</b> '
                f'contra a condição — razão <b>{razao:.1f}×</b>. Limite de '
                f'σ_res desta fonte: <b>{lim_sd:.4f}</b>.',
                aviso=(razao > 3.0)))
    n_ok = sum(1 for c in comp if c.source == fonte
               and rh._tripe_ok(res.get(c.case_id), lim_sd))
    n_tot = sum(1 for c in comp if c.source == fonte)
    corpo = (f'<h1>{_esc.escape(fonte)} — modelo contra as réplicas</h1>'
             f'<p class="sub">A previsão do modelo contra <b>todas</b> as '
             f'réplicas de cada condição, e o erro contra cada uma. A fonte fecha '
             f'<b>{n_ok}/{n_tot}</b> no tripé.</p>'
             f'<p class="nav"><a href="index.html">&larr; metodologia de '
             f'extração</a></p>' + "".join(blocos))
    return pagina(f"{fonte} — réplicas", corpo)


def main():
    comp, res, pisos = carrega()
    SAIDA.mkdir(parents=True, exist_ok=True)
    (SAIDA / "index.html").write_text(metodologia(comp, res, pisos),
                                      encoding="utf-8", newline="")
    print(f"index.html  (curva de referencia: {REF})")
    fams = familias(comp, res)
    por_fonte = collections.defaultdict(list)
    for k, cids in fams.items():
        por_fonte[k[0]].append(sorted(cids))
    n = 0
    for fonte, conds in sorted(por_fonte.items()):
        html = pagina_replicas(fonte, conds, res, pisos, comp)
        (SAIDA / f"replicas_{fonte}.html").write_text(html, encoding="utf-8",
                                                      newline="")
        n += 1
        print(f"  replicas_{fonte}.html  ({len(conds)} condicao(oes), "
              f"{sum(len(c) for c in conds)} curvas)")
    # indice das replicas na propria pagina de metodologia
    links = "".join(
        f'<li><a href="replicas_{f}.html">{_esc.escape(f)}</a> — '
        f'{len(c)} condição(ões), {sum(len(x) for x in c)} curvas</li>'
        for f, c in sorted(por_fonte.items()))
    idx = (SAIDA / "index.html").read_text(encoding="utf-8")
    idx = idx.replace("</div></body>",
                      f'<h2>10. Fontes com réplica</h2>'
                      f'<p>Uma página por fonte, com a previsão do modelo contra '
                      f'<b>todas</b> as réplicas e o erro contra cada uma:</p>'
                      f'<ul>{links}</ul></div></body>')
    (SAIDA / "index.html").write_text(idx, encoding="utf-8", newline="")
    print(f"\n{n + 1} paginas em {SAIDA}")


if __name__ == "__main__":
    main()
