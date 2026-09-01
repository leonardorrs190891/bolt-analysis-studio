# -*- coding: utf-8 -*-
"""Reports HTML de validacao (spec §3) — port de
New_Theory/generate_case_reports.py estendido aos 128 casos com degradacao
honesta + secao NOVA de decomposicao por mecanismo (pedido do professor
2026-07-10). Report geral com estatisticas globais e pisos de repetibilidade."""
from __future__ import annotations

import base64
import html as _esc
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

from ..calibration import knowledge_base as kb
from ..calibration.profiles import load_shared_material
from .case_registry import CaseRecord, all_records
from .inputs import geometry_for_case, inputs_for, load_full_curve, repo_root
from .runner import CaseResult

NICE = {
    "LIU_2025": "Liu 2025 — M16 shear (Sci. Rep.)",
    "YANG_2019": "Yang 2019 — M10 variable-amplitude (Shock & Vib.)",
    "YANG_2021": "Yang 2021 — M12 combined excitation (Shock & Vib.)",
    "YANG_2023_IJPEM": "Yang 2023 — M8 (IJPEM)",
    "ROUSSEAU_2025": "Rousseau 2025 — M12 (Materials)",
    "KARLSEN_2022": "Karlsen & Lemu 2022 — M30/M42 large bolts",
    "LU_2024": "Lu 2024 — M8 amplitude/torque sweeps (Sensors)",
    "ICMEZ_2025": "Icmez/Demir 2024-25 — M12 grip/force (EJRND)",
    "BAUER_2024": "Bauer 2024 — M8/M12 spectrum (Eng. Fail. Anal.)",
    "LIU_2022_RETIGHT": "Liu 2022 — retightening (Int. J. Struct.)",
    "LIU_2017_AXIAL": "Liu 2017 — axial sweeps (Tribol. Int.)",
    "LI_2022_MARSTRUC": "Li 2022 — contact creep (Mar. Struct.)",
    "LI_2022_TRIBOINT": "Li 2022 — axial x frequency, Ti (Tribol. Int.)",
    "SANDIA_2021": "Sandia 2021 — C-beam modal",
    # Rodada 4 (ingestao 2026-07-14)
    "LIU_2016": "Liu 2016 — M12 axial torque/amplitude (Wear)",
    "CHU_2026": "Chu 2026 — MJ10 superligas Junker (Tribol. Int.)",
    "ECCLES_2010": "Eccles 2010 — M8 prevailing-torque (Proc IMechE C)",
    "YANG_2023_AME": "Yang 2023 — MJ6 jet nut CFRP axial (Adv. Mech. Eng.)",
    "SUN_2025_CRIMP": "Sun 2025 — M8 crimp vs standard (Eng. Fail. Anal. 169)",
    "SUN_2025_REASSY": "Sun 2025 — MJ8 remontagens (Eng. Fail. Anal. 182)",
    "GRZEJDA_2026": "Grzejda 2026 — M10 multi-parafuso, benchmark nulo (Materials)",
    "JCSR_2023": "Yang/Bai/Ding 2023 — M20 relaxação x ambiente (JCSR)",
    "CACCESE_2009": "Caccese 2009 — 1/2-3/4 UNC composto/metal (Compos. Struct.)",
    "QIN_2024": "Qin 2024 — M6 CFRP-Ti interference-fit (Appl. Compos. Mater.)",
}
# constantes per-rig adotadas (adopted_configs) — proveniencia p/ exibicao
PROV = {
    "c_bend": "fitado-this-rig (compliance transversal, §4.35)",
    "loose_arrest_floor": "lido-do-dado (piso do platô final)",
    "k_ratchet": "fitado-this-rig (ratchet cinemático, §4.15)",
    "delta_free": "lido-do-dado (take-up, regressão de onset §4.19)",
    "k_wear_scale_tr": "fitado-this-rig (LEGADO → k_wear_spec, §4.42)",
    "emb_um": "handbook VDI (Rz) ou data-implícito da queda-inicial (L24, §4.40)",
    "dmg_gross_exp": "compartilhado (onset contínuo de dano, §4.33)",
    "slip_onset_W": "lido-do-dado (incubação, ciclo do platô)",
    "W_crit": "lido-do-dado (energia no joelho medido)",
}
SHARED_PROV = {
    "k_wear_spec": "Estágio A compartilhada — razão K/H [1/Pa] (merge §4.42a)",
    "C_creep": "Estágio A compartilhada — por par tribológico (§4.7)",
    "tr_loose_gain": "Estágio A compartilhada (âncora pendente §4.42)",
    "N_emb": "Estágio A compartilhada (constante de tempo do assentamento)",
    "W_conf_ref": "Estágio A — conformação, por par UFU (§4.9)",
    "conform_pressure_exp": "fixo n=2 (VDI)",
    "p_ref_conform": "computado do %yield (pct/70, roadmap 11f)",
}
# pisos de repetibilidade MEDIDOS (port de New_Theory/convergence_indicator.py
# FLOORS — MAE pareado entre repeats do proprio dado; limite fisico do fit)
# ("LU_2024","fig20"): 0.093 REMOVIDO em 2026-07-31: a leitura do paper provou
# que a fig20 NAO contem replicas (5 torques distintos na MESMA amplitude
# 1,0 mm) — qualquer pareamento intra-fig20 mede cruzamento de CONDICAO, nao
# repetibilidade (mesma causa-raiz do piso invalido retratado no mesmo dia;
# `lu2024_plano_melhoria.md` A2). O piso valido da fonte depende da Fig. 14
# (3 replicas reais documentadas, ainda nao digitalizadas).
FLOORS = {("BAUER_2024", "fig6"): 0.115, ("BAUER_2024", "fig8"): 0.093,
          ("KARLSEN_2022", ""): 0.115,
          ("YANG_2019", ""): 0.081}
_FAM_PT = {"transverse": "transversal", "axial": "axial", "creep": "creep",
           "other": "outra"}
_CLASS_PT = {"full_curve": "curva completa", "final_ratio": "só ratio final"}
_DECOMP_COLORS = {"embedding": "#2f6f8f", "creep": "#8f6f2f",
                  "wear": "#b3452c", "rotational_loosening": "#5f8f2f",
                  "thread_fretting": "#7f5fa0", "fatigue": "#a05f5f"}


def floor_of(source: str, case_id: str) -> float:
    for (src, tok), f in FLOORS.items():
        if source == src and (tok == "" or tok in case_id):
            return f
    return 0.0


def _fnum(v, unit=""):
    if v is None:
        return "—"
    if isinstance(v, float):
        if v == 0:
            return "0" + (" " + unit if unit else "")
        a = abs(v)
        s = f"{v:.4g}" if (a >= 1e-3 and a < 1e5) else f"{v:.3e}"
    else:
        s = str(v)
    return s + (" " + unit if unit else "")


def _row(label, value, prov=""):
    p = f'<span class="pv">{prov}</span>' if prov else ""
    return f'<tr><td class="k">{label}</td><td class="v">{value}</td><td>{p}</td></tr>'


# ---------------------------------------------------------------- SVG plots

def _stage_maes(cd, rd, pred):
    """MAE por estagio (janelas de ciclo 0-10% / 10-70% / 70-100% — proxy das
    fases assentamento/perda/cauda). None quando a janela nao tem pontos."""
    cd = np.asarray(cd)
    if not len(cd):
        return {"I": None, "II": None, "III": None}
    span = (cd[-1] - cd[0]) or 1.0
    frac = (cd - cd[0]) / span
    err = np.abs(np.asarray(pred) - np.asarray(rd))
    out = {}
    for name, lo, hi in (("I", 0.0, 0.10), ("II", 0.10, 0.70), ("III", 0.70, 1.001)):
        m = (frac >= lo) & (frac < hi)
        out[name] = float(err[m].mean()) if m.any() else None
    return out



def _error_narrative(result, dx, dy, pred):
    """`pred` = modelo JA alinhado nas abscissas `dx` (result.metric_pred).
    Nao reinterpolar aqui: a grade amostrada diverge da que a metrica usou."""
    if result.mae is None:
        return ""
    bits = [f"Em média o modelo erra <b>{100*result.mae:.1f} pontos "
            f"percentuais</b> de F/F&#8320; (MAE {result.mae:.4f})"]
    if result.maxerr is not None:
        bits.append(f"pior ciclo: {result.maxerr:.3f} @ N={int(result.maxerr_at or 0)}")
    if len(dx) and len(pred):
        resid = np.asarray(pred) - np.asarray(dy)
        frac_over = float((resid > 0).mean())
        lean = ("o modelo sobre-prediz F/F&#8320; (afrouxamento mais lento que "
                "o artigo) na maior parte da curva" if frac_over > 0.6 else
                "o modelo sub-prediz F/F&#8320; (afrouxamento mais rápido que "
                "o artigo) na maior parte da curva" if frac_over < 0.4 else
                "erro equilibrado entre sobre e sub-predição")
        bits.append(lean)
    if result.final_pred is not None and result.final_data is not None:
        bits.append(f"no fim do ensaio: modelo {result.final_pred:.3f} vs "
                    f"artigo {result.final_data:.3f} "
                    f"(&#916; {result.final_pred-result.final_data:+.3f})")
    return "<p class='narr'>" + " · ".join(bits) + ".</p>"


def _aligned_model_xy(result, mx, my_raw):
    """Curva do modelo COMO A METRICA A VE: dividida pelo divisor de
    alinhamento e ancorada no 1o ciclo do dado.

    Antes da ancora `n0` a divisao nao tem sentido (`my_raw/align` sobe acima
    de 1 — e' a queda de assentamento que o dado nunca viu, dividida por si
    mesma), entao a serie COMECA em (n0, 1.0), que vale por construcao.
    Sem `align` gravado (stores < 2026-07-27) devolve a curva crua.
    """
    align = float(result.align) if result.align else 1.0
    if align == 1.0:
        return list(map(float, mx)), list(map(float, my_raw)), align
    n0 = float(result.metric_x[0]) if result.metric_x else 0.0
    xs, ys = [n0], [1.0]
    for xv, yv in zip(mx, my_raw):
        if float(xv) > n0:
            xs.append(float(xv))
            ys.append(float(yv) / align)
    return xs, ys, align


def _metric_window_note(align: float, trim_n, dx, dy) -> str:
    """Explica, com os numeros DESTE caso, as duas convencoes que separam a
    curva medida do que a metrica pontua: o ALINHAMENTO e o TRIM.

    Existe porque ate 2026-07-27 nenhuma das duas aparecia na pagina — o
    cabecalho trazia um MAE alinhado+trimado sobre um grafico cru e integral,
    e os MAEs por estagio (crus, sem trim) davam ~10x o cabecalho no mesmo
    documento (li2022ti full: 0.0317 vs 0.19/0.30/0.28)."""
    parts = []
    if align != 1.0:
        parts.append(
            f"<b>Alinhamento ÷{align:.4f}.</b> O artigo normaliza F/F₀ = 1 no "
            f"primeiro ponto medido, então a perda que o modelo acumula "
            f"<i>antes</i> desse ciclo (assentamento) não tem contraparte no "
            f"dado. A métrica divide a curva do modelo por seu próprio valor "
            f"ali — aqui {align:.4f}, isto é "
            f"<b>{100*(1-align):.1f} pontos percentuais</b> de queda que a "
            f"métrica não pontua. A linha cheia é a curva alinhada (a que o "
            f"MAE mede); a tracejada cinza é a crua do engine.")
    if trim_n is not None and len(dx) >= 2:
        ax, ay = np.asarray(dx, dtype=float), np.asarray(dy, dtype=float)
        inside = ax <= trim_n
        frag = ""
        if inside.any() and not inside.all():
            r_tr, r_end = float(ay[inside][-1]), float(ay[-1])
            loss_tot, loss_cut = float(ay[0]) - r_end, r_tr - r_end
            if loss_tot > 1e-9:
                frag = (f" O trecho excluído carrega "
                        f"<b>{100*loss_cut/loss_tot:.0f}% da perda de "
                        f"pré-carga medida</b> nesta curva "
                        f"(F/F₀ vai de {r_tr:.3f} a {r_end:.3f} depois do corte).")
        parts.append(
            f"<b>Trim em N = {int(trim_n):,}</b>".replace(",", " ") +
            f". A métrica só pontua N ≤ {int(trim_n):,}".replace(",", " ") +
            f"; a faixa avermelhada à direita é trecho declarado fora-do-modelo "
            f"(exceção registrada no cfg adotado, sujeita a ratificação).{frag}")
    if not parts:
        return ""
    return ("<p class='narr' style='border-left:3px solid var(--err);"
            "padding-left:10px'>" + " ".join(parts) + "</p>")


def _decomp_section(result: CaseResult) -> str:
    if not result.ok:
        return ""
    if not result.decomp:
        return ('<h2 id="sec4">4. Decomposição por mecanismo</h2>'
                '<p class="verd">Resultado de snapshot da campanha — '
                're-simule o caso para obter a decomposição por mecanismo.</p>')
    finals = {m: v[-1] for m, v in result.decomp.items()}
    tot = max(sum(finals.values()), 1e-12)
    rows = "".join(
        _row(f'<span style="color:{_DECOMP_COLORS.get(m, "#888")}">&#9632;</span> {m}',
             f"{v:.4f}", f"{100*v/tot:.1f}% da perda")
        for m, v in sorted(finals.items(), key=lambda kv: -kv[1]))
    mechs = [m for m in _DECOMP_COLORS if m in result.decomp]
    mechs += [m for m in result.decomp if m not in mechs]
    stack_chart = _chart_div(dict(
        type="stack", h=260, xlabel="ciclos N",
        ylabel="perda F/F₀ cumulativa", name=f"{result.case_id}_decomposicao",
        series=[dict(name=m, color=_DECOMP_COLORS.get(m, "#888888"),
                     x=list(map(float, result.cycles)),
                     y=list(map(float, result.decomp[m])))
                for m in mechs]))
    return (f'<h2 id="sec4">4. Decomposição por mecanismo</h2>{stack_chart}'
            f'<table>{rows}</table>'
            f'<p class="sub2">soma dos mecanismos = perda total '
            f'{tot:.4f} = 1 &#8722; F/F&#8320; final (fechamento exato do engine)</p>')


def _data_points(rec: CaseRecord):
    """(dx, dy) da referencia: CSV completo ou pontos experimentais esparsos."""
    if rec.case_class == "full_curve" and rec.csv_path is not None:
        try:
            rel = rec.csv_path.relative_to(repo_root()).as_posix()
        except ValueError:                # caso do usuario fora do repo
            rel = str(rec.csv_path)
        cyc, r = load_full_curve(rel)
        off = float(getattr(rec.validation_case, "csv_x_offset", 0.0) or 0.0)
        sc = float(getattr(rec.validation_case, "csv_x_scale", 1.0) or 1.0)
        return np.maximum(cyc - off, 0.0) * sc, r / max(r[0], 1e-9)
    pts = getattr(rec.validation_case, "experimental_data", []) or []
    if pts:
        return (np.array([p.cycles for p in pts], dtype=float),
                np.array([p.preload_ratio for p in pts], dtype=float))
    return np.array([]), np.array([])


data_points = _data_points            # API publica p/ o browser (Plano B)

# Barra superior fixa (report v3): titulo + badge + Imprimir/PDF + controle de
# tema (auto -> escuro -> claro, persistido; tokens claro/escuro ja existem no
# _CSS). Inline e self-contained (funciona em file://).
_THEME_JS = """<script>(function(){
var KEY='bas_report_theme', order=['auto','dark','light'],
    root=document.documentElement, btn=document.getElementById('thbtn'),
    label={auto:'auto',dark:'escuro',light:'claro'};
function apply(v){
  if(v==='auto'){delete root.dataset.theme;}else{root.dataset.theme=v;}
  btn.textContent='tema: '+label[v];}
var cur=localStorage.getItem(KEY)||'auto';
if(order.indexOf(cur)<0){cur='auto';}
apply(cur);
btn.addEventListener('click',function(){
  cur=order[(order.indexOf(cur)+1)%order.length];
  localStorage.setItem(KEY,cur);apply(cur);});
})();</script>"""


def _topbar(title: str, badge_html: str = "") -> str:
    return (f'<div class="topbar"><span class="tb-title">{title}</span>'
            f'{badge_html}<span class="tb-right">'
            f'<button type="button" class="cbtn" onclick="window.print()">'
            f'Imprimir/PDF</button>'
            f'<button id="thbtn" type="button" aria-label="alternar tema">'
            f'tema: auto</button></span></div>' + _THEME_JS)


def _chart_div(cfg: dict, extra: str = "") -> str:
    """Grafico interativo (report v3): dados embutidos em data-chart; o
    renderer BASCHART (JS puro, inline) desenha no load — tooltip, legenda
    clicavel, zoom por arrasto, CSV."""
    payload = _esc.escape(json.dumps(cfg, separators=(",", ":")), quote=True)
    return (f'<div class="chart-box {extra}">'
            f'<div class="chart" data-chart="{payload}"></div></div>')


_CHART_JS = r"""<script>/* BASCHART v1 — renderer interativo embutido (JS puro,
sem dependencias; file:// e impressao ok). Tooltip+crosshair, legenda clicavel,
zoom por arrasto no eixo x (duplo-clique reseta), download CSV por grafico. */
(function(){
'use strict';
var NS='http://www.w3.org/2000/svg';
function el(t,a){var e=document.createElementNS(NS,t);
 for(var k in a)e.setAttribute(k,a[k]);return e;}
function fmt(v,d){if(v==null||isNaN(v))return'–';var a=Math.abs(v);
 if(a!==0&&(a<1e-3||a>=1e5))return v.toExponential(2);
 return v.toFixed(d==null?3:d);}
function interp(xs,ys,x){var n=xs.length;if(!n)return null;
 if(x<=xs[0])return ys[0];if(x>=xs[n-1])return ys[n-1];
 var lo=0,hi=n-1;while(hi-lo>1){var m=(hi+lo)>>1;if(xs[m]<=x)lo=m;else hi=m;}
 var t=(x-xs[lo])/(xs[hi]-xs[lo]||1);return ys[lo]+t*(ys[hi]-ys[lo]);}
function render(box){
 var cfg=JSON.parse(box.dataset.chart);
 var W=cfg.w||560,H=cfg.h||300,ML=56,MR=16,MT=14,MB=40;
 var hidden={},zx=null,drag=null;
 var wrap=box.parentElement;wrap.style.position='relative';
 var tip=document.createElement('div');tip.className='ctip';
 tip.style.display='none';wrap.appendChild(tip);
 function xext(){var lo=Infinity,hi=-Infinity;
  cfg.series.forEach(function(s){if(hidden[s.name]||!s.x.length)return;
   lo=Math.min(lo,s.x[0]);hi=Math.max(hi,s.x[s.x.length-1]);});
  if(!isFinite(lo)){lo=0;hi=1;}return zx||[lo,hi];}
 function draw(){
  var ex=xext(),x0=ex[0],x1=ex[1];
  var svg=el('svg',{viewBox:'0 0 '+W+' '+H,'class':'plot'});
  var X;
  if(cfg.xlog){var l0=Math.log10(Math.max(x0,1)),l1=Math.log10(Math.max(x1,10));
   X=function(v){return ML+(Math.log10(Math.max(v,1))-l0)/((l1-l0)||1)*(W-ML-MR);};}
  else{X=function(v){return ML+(v-x0)/((x1-x0)||1)*(W-ML-MR);};}
  var ymin=0,ymax=cfg.ymax||0,i;
  if(cfg.type==='stack'){ymax=0;
   var n=cfg.series[0]?cfg.series[0].x.length:0;
   for(i=0;i<n;i++){var tot=0;cfg.series.forEach(function(s){
    if(!hidden[s.name])tot+=s.y[i];});ymax=Math.max(ymax,tot);}
   ymax=(ymax||1e-6)*1.1;}
  else if(cfg.sym){var m=0;cfg.series.forEach(function(s){
   if(hidden[s.name])return;s.y.forEach(function(v){m=Math.max(m,Math.abs(v));});});
   m=Math.max(m,cfg.band||0)*1.15;if(!m)m=1e-6;ymin=-m;ymax=m;}
  else if(!ymax){cfg.series.forEach(function(s){if(hidden[s.name])return;
   s.y.forEach(function(v){ymax=Math.max(ymax,v);});});ymax=(ymax||1)*1.08;}
  var Y=function(v){return MT+(1-(v-ymin)/((ymax-ymin)||1))*(H-MT-MB);};
  var g;for(g=0;g<=4;g++){var yv=ymin+(ymax-ymin)*g/4,yy=Y(yv);
   svg.appendChild(el('line',{x1:ML,y1:yy,x2:W-MR,y2:yy,'class':'gl'}));
   var t=el('text',{x:ML-6,y:yy+3,'text-anchor':'end','class':'tk'});
   t.textContent=fmt(yv,cfg.sym?3:2);svg.appendChild(t);}
  for(g=0;g<=4;g++){var xv=x0+(x1-x0)*g/4;
   var t2=el('text',{x:X(xv),y:H-MB+14,'text-anchor':'middle','class':'tk'});
   t2.textContent=Math.round(xv).toLocaleString();svg.appendChild(t2);}
  if(cfg.sym)svg.appendChild(el('line',{x1:ML,y1:Y(0),x2:W-MR,y2:Y(0),'class':'zl'}));
  if(cfg.band)svg.appendChild(el('rect',{x:ML,y:Y(cfg.band),width:W-ML-MR,
   height:Math.max(Y(-cfg.band)-Y(cfg.band),1),'class':'band'}));
  /* fronteira do TRIM: a metrica so olha N <= vline; a direita e' fora-da-metrica */
  if(cfg.vline!=null&&cfg.vline>x0&&cfg.vline<x1){
   svg.appendChild(el('rect',{x:X(cfg.vline),y:MT,
    width:Math.max(X(x1)-X(cfg.vline),0),height:H-MT-MB,'class':'trimz'}));
   svg.appendChild(el('line',{x1:X(cfg.vline),y1:MT,x2:X(cfg.vline),y2:H-MB,
    'class':'triml'}));
   var tv=el('text',{x:X(cfg.vline)+4,y:MT+11,'class':'tk'});
   tv.textContent='fora da métrica (trim)';svg.appendChild(tv);}
  function clip(s){var xs=[],ys=[],j;for(j=0;j<s.x.length;j++){
   if(s.x[j]>=x0&&s.x[j]<=x1){xs.push(s.x[j]);ys.push(s.y[j]);}}
   return[xs,ys];}
  if(cfg.type==='stack'){var base=null;
   cfg.series.forEach(function(s){if(hidden[s.name])return;
    var c=clip(s),xs=c[0],ys=c[1];
    if(!base){base=xs.map(function(){return 0;});}
    var top=ys.map(function(v,j){return base[j]+v;});
    var pts='';xs.forEach(function(x,j){pts+=X(x)+','+Y(top[j])+' ';});
    for(var j2=xs.length-1;j2>=0;j2--)pts+=X(xs[j2])+','+Y(base[j2])+' ';
    var poly=el('polygon',{points:pts,'fill-opacity':'0.75',stroke:'none'});
    poly.style.fill=s.color;svg.appendChild(poly);base=top;});}
  else{cfg.series.forEach(function(s){if(hidden[s.name])return;
   var c=clip(s),xs=c[0],ys=c[1];
   if(s.points){xs.forEach(function(x,j){var d=el('circle',
    {cx:X(x),cy:Y(ys[j]),r:2.6});d.style.fill=s.color;svg.appendChild(d);});}
   if(!s.points||s.line){var pl='';
    xs.forEach(function(x,j){pl+=X(x)+','+Y(ys[j])+' ';});
    var p=el('polyline',{points:pl,fill:'none','stroke-width':'2.2'});
    if(s.dash){p.setAttribute('stroke-dasharray','5,4');
     p.setAttribute('stroke-width','1.6');}
    p.style.stroke=s.color;svg.appendChild(p);}});}
  var xl=el('text',{x:(ML+W-MR)/2,y:H-4,'text-anchor':'middle','class':'axl'});
  xl.textContent=cfg.xlabel||'';svg.appendChild(xl);
  var yl=el('text',{x:13,y:(MT+H-MB)/2,'text-anchor':'middle','class':'axl',
   transform:'rotate(-90 13 '+((MT+H-MB)/2)+')'});
  yl.textContent=cfg.ylabel||'';svg.appendChild(yl);
  var cross=el('line',{x1:-9,y1:MT,x2:-9,y2:H-MB,'class':'zl',opacity:'0.5'});
  svg.appendChild(cross);
  var selr=el('rect',{x:0,y:MT,width:0,height:H-MT-MB,'class':'band'});
  svg.appendChild(selr);
  box.innerHTML='';box.appendChild(svg);
  function dataX(ev){var r=svg.getBoundingClientRect();
   var px=(ev.clientX-r.left)/r.width*W;var f=(px-ML)/((W-ML-MR)||1);
   if(cfg.xlog){var a0=Math.log10(Math.max(x0,1)),a1=Math.log10(Math.max(x1,10));
    return Math.pow(10,a0+f*(a1-a0));}
   return x0+f*(x1-x0);}
  svg.addEventListener('mousemove',function(ev){var xv=dataX(ev);
   if(xv<x0||xv>x1){tip.style.display='none';
    cross.setAttribute('x1',-9);cross.setAttribute('x2',-9);return;}
   cross.setAttribute('x1',X(xv));cross.setAttribute('x2',X(xv));
   var rows=[(cfg.xname||'N')+' ≈ '+Math.round(xv).toLocaleString()];
   if(cfg.type==='stack'){var tt=0;
    cfg.series.forEach(function(s){if(hidden[s.name])return;
     var v=interp(s.x,s.y,xv);tt+=v;
     rows.push('<span style="color:'+s.color+'">■</span> '+s.name+': '+fmt(v,4));});
    rows.push('<b>total: '+fmt(tt,4)+'</b>');}
   else{cfg.series.forEach(function(s){if(hidden[s.name])return;
    rows.push('<span style="color:'+s.color+'">■</span> '+s.name+': '+
     fmt(interp(s.x,s.y,xv),4));});}
   tip.innerHTML=rows.join('<br>');tip.style.display='block';
   var wr=wrap.getBoundingClientRect();
   tip.style.left=Math.min(ev.clientX-wr.left+14,Math.max(wr.width-180,0))+'px';
   tip.style.top=(ev.clientY-wr.top+10)+'px';
   if(drag!=null){var a=X(Math.min(drag,xv)),b=X(Math.max(drag,xv));
    selr.setAttribute('x',a);selr.setAttribute('width',Math.max(b-a,0));}});
  svg.addEventListener('mouseleave',function(){tip.style.display='none';
   cross.setAttribute('x1',-9);cross.setAttribute('x2',-9);});
  svg.addEventListener('mousedown',function(ev){drag=dataX(ev);ev.preventDefault();});
  svg.addEventListener('mouseup',function(ev){if(drag==null)return;
   var b=dataX(ev);
   if(Math.abs(b-drag)>(x1-x0)*0.02){zx=[Math.min(drag,b),Math.max(drag,b)];}
   drag=null;draw();});
  svg.addEventListener('dblclick',function(){zx=null;draw();});
 }
 var bar=document.createElement('div');bar.className='cbar';
 cfg.series.forEach(function(s){var it=document.createElement('span');
  it.className='citem';
  it.innerHTML='<span class="sw" style="background:'+s.color+'"></span>'+s.name;
  it.addEventListener('click',function(){hidden[s.name]=!hidden[s.name];
   it.classList.toggle('off',!!hidden[s.name]);draw();});
  bar.appendChild(it);});
 var dl=document.createElement('button');dl.type='button';dl.className='cbtn';
 dl.textContent='Baixar dados (CSV)';
 dl.addEventListener('click',function(){var lines=[];
  cfg.series.forEach(function(s){lines.push('# '+s.name);lines.push('x,y');
   s.x.forEach(function(x,j){lines.push(x+','+s.y[j]);});});
  var a=document.createElement('a');
  a.href='data:text/csv;charset=utf-8,'+encodeURIComponent(lines.join('\n'));
  a.download=(cfg.name||'grafico')+'.csv';a.click();});
 bar.appendChild(dl);
 var hint=document.createElement('span');hint.className='chint';
 hint.textContent='arraste p/ zoom · duplo-clique reseta · legenda oculta séries';
 bar.appendChild(hint);
 wrap.appendChild(bar);
 draw();
}
document.querySelectorAll('.chart').forEach(render);
})();</script>"""

_PAGE_JS = r"""<script>/* BASPAGE v1 — TOC ativo + secoes colapsaveis */
(function(){
'use strict';
var hs=Array.prototype.slice.call(document.querySelectorAll('h2[id^="sec"]'));
hs.forEach(function(h){
 var body=document.createElement('div');body.className='secbody';
 var n=h.nextSibling;
 while(n&&!(n.nodeType===1&&n.tagName==='H2')){var nx=n.nextSibling;
  body.appendChild(n);n=nx;}
 h.parentNode.insertBefore(body,h.nextSibling);
 h.classList.add('collapsible');
 h.addEventListener('click',function(){h.classList.toggle('closed');
  body.style.display=h.classList.contains('closed')?'none':'';});});
var links=Array.prototype.slice.call(
 document.querySelectorAll('.toc a[href^="#sec"]'));
if('IntersectionObserver' in window&&links.length){
 var map={};links.forEach(function(a){map[a.getAttribute('href').slice(1)]=a;});
 var io=new IntersectionObserver(function(es){es.forEach(function(e){
  if(e.isIntersecting){links.forEach(function(a){a.classList.remove('on');});
   var a=map[e.target.id];if(a)a.classList.add('on');}});},
  {rootMargin:'-20% 0px -70% 0px'});
 hs.forEach(function(h){io.observe(h);});}
})();</script>"""

_TIP_JS = r"""<script>/* BASTIP v1 — tooltip dos selos (2026-07-31).

   Tres decisoes que sao consequencia de restricao medida, nao gosto:

   (a) `position:fixed` no BODY, nunca absoluto no selo. Os selos vivem dentro
       de `div.ovx` com `overflow-x:auto`; um tooltip absoluto seria RECORTADO
       pela caixa de rolagem — e, pior, faria a tabela ganhar barra horizontal
       ao aparecer.
   (b) delegacao no documento, nao um listener por selo. Sao ~800 selos
       desenhados; 800 pares de listeners e desperdicio puro.
   (c) NENHUM `setPointerCapture`. Com captura ativa o navegador retargeta o
       `click` para quem capturou, e isso MATOU o link dos pontos do 3D em
       2026-07-29 (registrado no CLAUDE.md). O selo fica ao lado de um `<a>`
       para `reports/<cid>.html`; um tooltip nao pode roubar esse clique. */
(function(){
'use strict';
var box=null,alvo=null;
function cria(){
 if(box){return box;}
 box=document.createElement('div');box.className='tipbox';
 box.setAttribute('role','tooltip');box.hidden=true;
 document.body.appendChild(box);return box;}
function posiciona(el){
 var r=el.getBoundingClientRect(),b=box.getBoundingClientRect(),M=8;
 /* acima por default; abaixo se nao couber (o rodape da pagina e' comprido) */
 var top=r.top-b.height-M;
 if(top<M){top=r.bottom+M;}
 var left=r.left+r.width/2-b.width/2;
 left=Math.max(M,Math.min(left,window.innerWidth-b.width-M));
 box.style.top=Math.round(top)+'px';box.style.left=Math.round(left)+'px';}
function mostra(el){
 var t=el.getAttribute('data-tip');if(!t){return;}
 alvo=el;cria();
 var x=el.getAttribute('data-tipx');
 box.textContent='';
 var p=document.createElement('div');p.className='tip-b';p.textContent=t;
 box.appendChild(p);
 if(x){var q=document.createElement('div');q.className='tip-x';
       q.textContent=x;box.appendChild(q);}
 box.hidden=false;box.style.top='-9999px';box.style.left='0px';
 posiciona(el);}
function esconde(){if(box){box.hidden=true;}alvo=null;}
document.addEventListener('pointerover',function(e){
 var el=e.target.closest?e.target.closest('[data-tip]'):null;
 if(el&&el!==alvo){mostra(el);}else if(!el&&alvo){esconde();}});
document.addEventListener('pointerdown',function(e){
 /* toque: `pointerover` dispara no tap, mas o proximo tap em outro lugar tem
    de fechar — sem isto o tooltip fica preso na tela em telefone. */
 var el=e.target.closest?e.target.closest('[data-tip]'):null;
 if(!el){esconde();}});
document.addEventListener('focusin',function(e){
 var el=e.target.closest?e.target.closest('[data-tip]'):null;
 if(el){mostra(el);}else{esconde();}});
document.addEventListener('focusout',esconde);
document.addEventListener('keydown',function(e){
 if(e.key==='Escape'){esconde();}});
/* rolagem/resize invalidam a posicao FIXA; recolocar e' mais barato que
   recalcular a cada frame, e fechar no scroll da caixa de rolagem evita o
   tooltip "flutuando" longe do selo que o gerou. */
window.addEventListener('scroll',function(){if(alvo){posiciona(alvo);}},true);
window.addEventListener('resize',function(){if(alvo){posiciona(alvo);}});
})();</script>"""


_MASTER_JS = r"""<script>/* BASMASTER v2 — texto + filtros rapidos + ordenacao */
(function(){
'use strict';
var inp=document.getElementById('filtro');
var flag='';
function apply(){
 var q=inp?inp.value.toLowerCase():'';
 document.querySelectorAll('table.idx tbody tr').forEach(function(tr){
  var okq=tr.textContent.toLowerCase().indexOf(q)>=0;
  var fl=tr.getAttribute('data-flags');
  /* linhas sem data-flags (orcamento, marcos do ledger) respondem so ao
     texto — um filtro rapido nao deve esvaziar aquelas tabelas. */
  var okf=(!flag||fl===null)?true:fl.split(' ').indexOf(flag)>=0;
  tr.style.display=(okq&&okf)?'':'none';});}
if(inp){inp.addEventListener('input',apply);}
document.querySelectorAll('button.qf').forEach(function(b){
 b.addEventListener('click',function(){
  var f=b.getAttribute('data-f')||'';
  flag=(flag===f)?'':f;
  document.querySelectorAll('button.qf').forEach(function(x){
   if(flag&&x.getAttribute('data-f')===flag){x.classList.add('on');}
   else{x.classList.remove('on');}});
  var det=document.getElementById('tabelatodos');
  if(flag&&det){det.open=true;}
  apply();});});
document.querySelectorAll('table.idx th').forEach(function(th){
 th.style.cursor='pointer';th.title='clique para ordenar';
 th.addEventListener('click',function(){
  var tb=th.closest('table').tBodies[0];
  var idx=Array.prototype.indexOf.call(th.parentNode.children,th);
  var rows=Array.prototype.slice.call(tb.rows);
  var asc=th.dataset.asc!=='1';th.dataset.asc=asc?'1':'0';
  rows.sort(function(a,b){
   var x=a.cells[idx].textContent.trim(),y=b.cells[idx].textContent.trim();
   var nx=parseFloat(x),ny=parseFloat(y);
   var c=(!isNaN(nx)&&!isNaN(ny))?nx-ny:x.localeCompare(y);
   return asc?c:-c;});
  rows.forEach(function(r){tb.appendChild(r);});});});
})();</script>"""


# --- secao MSD reproduzivel (report v2, spec 2026-07-10-report-v2) ----------
_GLOSSARY = {
    "F₀": ("pré-carga inicial de aperto do parafuso", "N"),
    "F/F₀": ("razão de pré-carga retida (1 = aperto intacto, 0 = solto)", "–"),
    "δ (delta_amplitude)": ("amplitude do deslocamento transversal imposto (Junker)", "mm"),
    "F_amp": ("amplitude da força cíclica (modo força / axial)", "N"),
    "k": ("rigidez do elemento MSD", "N/m"),
    "c": ("amortecimento do elemento MSD", "N·s/m"),
    "m": ("massa do elemento MSD", "kg"),
    "k_b": ("rigidez axial do parafuso = E·A_s/L_eff", "N/m"),
    "A_s": ("área de tensão da rosca (ISO 898-1)", "mm²"),
    "L_eff": ("comprimento efetivo (grip) do parafuso", "mm"),
    "d₂": ("diâmetro de passo da rosca (ISO 724)", "mm"),
    "r_bearing / A_contact": ("raio efetivo e área real do anel de apoio da cabeça", "mm / mm²"),
    "µ": ("coeficiente de atrito (rosca = apoio neste modelo)", "–"),
    "Rz": ("classe de rugosidade das superfícies (tabela VDI de assentamento)", "µm"),
    "emb_depth": ("profundidade total de assentamento (embedding) da pilha", "m"),
    "N_emb": ("constante de tempo do assentamento (ciclos p/ ~63%)", "ciclos"),
    "C_creep": ("constante de creep do par tribológico (Norton)", "por par"),
    "k_wear_spec": ("desgaste específico K/H (Archard identificável)", "1/Pa"),
    "tr_loose_gain": ("ganho do afrouxamento rotacional transversal", "–"),
    "W_conf_ref": ("energia de referência da conformação dependente de pressão", "J"),
    "slip_onset_W": ("energia de incubação até o início do slip macroscópico", "J"),
    "c_bend": ("fator de rigidez de flexão do parafuso no k_tr", "–"),
    "loose_arrest_floor": ("piso de auto-travamento do afrouxamento", "F/F₀"),
    "k_ratchet": ("taxa do ratchet cinemático por ciclo de slip", "–"),
    "delta_free": ("folga/take-up antes do carregamento morder", "m"),
    "conform_driver / k_tr_mode / …": ("chaves de modo do engine V2 (formas ativas)", "–"),
}


def _svg_chain(elements, W=560):
    """Cadeia de elementos como no builder: caixas em coluna, conexao serie."""
    BH, GAP, BW = 30, 12, 300
    H = len(elements) * (BH + GAP) + GAP
    x = (W - BW) / 2
    s = [f'<svg viewBox="0 0 {W} {H}" class="plot chain" '
         f'xmlns="http://www.w3.org/2000/svg">']
    for i, el in enumerate(elements):
        y = GAP + i * (BH + GAP)
        typ = getattr(el.type, "name", str(el.type))
        s.append(f'<rect x="{x}" y="{y}" width="{BW}" height="{BH}" rx="6" '
                 f'class="box {"ground" if typ == "GROUND" else ""}"/>')
        s.append(f'<text class="bt" x="{W/2}" y="{y+BH/2+4}" text-anchor="middle">'
                 f'#{el.id} {typ} — {el.name or "–"}</text>')
        if i < len(elements) - 1:
            s.append(f'<line class="cn" x1="{W/2}" y1="{y+BH}" '
                     f'x2="{W/2}" y2="{y+BH+GAP}"/>')
    s.append('</svg>')
    return "".join(s)


def _msd_section(rec: CaseRecord, geom_rows: str = "") -> str:
    """Secao '2. Modelo MSD' do modelo REAL (build_case_model — o mesmo do
    'Abrir no Model/Run'), reproduzivel so lendo (spec §2.2). `geom_rows`
    opcional: linhas prontas da geometria do parafuso (sub-tabela)."""
    try:
        from .gui_bridge import build_case_model
        model = build_case_model(rec)
    except Exception as exc:
        return (f'<h2 id="sec2">2. Modelo MSD (junta)</h2><p class="verd">Modelo não '
                f'montável para este caso ({exc}) — carregamento não '
                f'parametrizado no runner v1.</p>')
    els = list(model.elements)
    rows = "".join(
        f'<tr><td>{e.id}</td><td>{getattr(e.type, "name", e.type)}</td>'
        f'<td>{e.name or "–"}</td><td class="v">{_fnum(e.msd.k)}</td>'
        f'<td class="v">{_fnum(e.msd.c)}</td><td class="v">{_fnum(e.msd.m)}</td>'
        f'<td>{getattr(e.material, "name", "–")}</td>'
        f'<td class="v">{_fnum(getattr(e, "preload_percent_yield", None))}</td></tr>'
        for e in els)
    gl = model.global_loading
    load_rows = [
        _row("Tipo de carga", getattr(getattr(gl, "type", None), "name",
                                      str(getattr(gl, "type", "–")))),
        _row("Modo de controle", getattr(gl, "control_mode", "–"),
             "displacement = Junker (δ imposto); force = servo-hidráulico"),
        _row("F₀ pré-carga", _fnum(getattr(gl, "F_preload", None), "N")),
        _row("Amplitude δ", _fnum(getattr(gl, "delta_amplitude", None), "mm")),
        _row("Frequência", _fnum(getattr(gl, "frequency", None), "Hz")),
        _row("N ciclos", _fnum(getattr(gl, "n_cycles", None))),
        _row("µ (atrito)", _fnum(getattr(gl, "mu_initial", None) or
                                 getattr(model, "mu_initial", None))),
    ]
    gloss = "".join(
        f'<tr><td class="k">{sym}</td><td>{desc}</td><td class="v">{unit}</td></tr>'
        for sym, (desc, unit) in _GLOSSARY.items())
    steps = ('<ol class="steps">'
             '<li><b>Pelo software:</b> módulo <i>Results → Validation</i>, '
             'selecionar o caso, <i>Abrir no Model/Run</i> — monta exatamente '
             'este modelo.</li>'
             '<li><b>Manualmente:</b> File → Nova Análise (wizard) com o '
             'parafuso acima; no PropertyInspector, aba Loading, aplicar a '
             'tabela de carregamento; aba Contact, aplicar µ; as constantes '
             'V2 da seção 5 entram como overrides de calibração e a '
             'geometria fina vem do caso.</li></ol>')
    geom_html = (f'<h3>Geometria do parafuso</h3><table>{geom_rows}</table>'
                 if geom_rows else "")
    return (f'<h2 id="sec2">2. Modelo MSD (junta) — como preparado no software</h2>'
            f'{_svg_chain(els)}'
            f'<h3>Elementos</h3>'
            f'<div class="ovx"><table class="wide"><thead><tr><th>id</th><th>tipo</th>'
            f'<th>nome</th><th>k [N/m]</th><th>c [N·s/m]</th><th>m [kg]</th>'
            f'<th>material</th><th>preload %yield</th></tr></thead>'
            f'<tbody>{rows}</tbody></table></div>'
            f'{geom_html}'
            f'<h3>Carregamento global</h3><table>{"".join(load_rows)}</table>'
            f'<h3>Glossário de variáveis</h3>'
            f'<div class="ovx"><table class="wide"><thead><tr><th>símbolo</th>'
            f'<th>descrição</th><th>unidade</th></tr></thead>'
            f'<tbody>{gloss}</tbody></table></div>'
            f'<h3>Para refazer no software</h3>{steps}')


def _paper_figs(source: str, case_id: str, figdir: Path):
    """Figuras do ARTIGO desta fonte, do acervo já extraído dos PDFs
    (`variable_explorer/paper_figures/<fonte_minuscula>__<painel>.png`).

    Devolve `[(arquivo, casou_por_painel)]`. O painel é casado pelo pedaço do
    nome depois de `__` aparecer no `case_id` (`bauer_2024__fig6` casa
    `bauer2024_M8_fig6_rep1`); quando não casa nenhum, devolve TODAS as figuras
    da fonte marcadas como não-casadas — melhor mostrar as duas e dizer que o
    painel não foi resolvido do que escolher a errada em silêncio."""
    if not figdir.is_dir():
        return []
    pre = source.lower() + "__"
    todas = sorted(p.name for p in figdir.glob("*.png")
                   if p.name.lower().startswith(pre))
    if not todas:
        return []
    cid = case_id.lower().replace("_", "").replace("-", "")
    casadas = [f for f in todas
               if f.lower()[len(pre):-4].replace("_", "") in cid]
    return ([(f, True) for f in casadas] if casadas
            else [(f, False) for f in todas])


_FIG_MAXW = 1100          # largura máxima embutida (mediana do acervo: 776 px)
_FIG_CORES = 128          # paleta do PNG indexado
_FIG_CACHE: Dict[str, str] = {}


def _fig_data_uri(p: Path) -> Optional[str]:
    """A figura do artigo como `data:` URI — **gravada dentro do HTML**, em vez
    de um `<img src="../../variable_explorer/paper_figures/...">`.

    Pedido do professor (2026-07-29): *"as figuras podem ficar gravadas no html
    de maneira permanente"*. E não era só conveniência — o link relativo estava
    **quebrado quando a página é servida**: a raiz do servidor é
    `validation_html/`, o `../../` sobe acima dela e o `http.server` normaliza os
    `..` fora por segurança ⇒ **HTTP 404** em todas as 195 páginas que têm
    figura, com o arquivo existindo no disco. E `<img>` que não carrega não
    reclama no console: quebrava calado. Embutido, funciona servido, em
    `file://`, dentro de um `.zip` e depois de mover a pasta.

    Formato: **PNG indexado em 128 cores** (não WebP/JPEG). Estas figuras são o
    instrumento de CONFERÊNCIA DA DIGITALIZAÇÃO (§3b) — comprimir com perda
    justamente o artefato que serve para verificar se a digitalização está certa
    é trocar a coisa medida pela medição. Medido no acervo de 49 figuras: o PNG
    indexado dá **erro médio < 1/255 por canal em TODAS**, e o total dos 203
    reports vai de 18,4 MB para ~37,5 MB (2,04×). WebP q80 daria 33,6 MB (1,83×)
    e não vale a perda; o PNG original daria 63,2 MB (3,44×).

    Degrada devolvendo `None` (sem Pillow, arquivo ilegível) — aí o chamador cai
    no `<img src>` relativo de antes, que é o comportamento velho, não um erro.
    """
    chave = str(p)
    if chave in _FIG_CACHE:
        return _FIG_CACHE[chave] or None
    try:
        from PIL import Image
        import io as _io
        im = Image.open(p)
        if im.width > _FIG_MAXW:
            im = im.resize((_FIG_MAXW, round(im.height * _FIG_MAXW / im.width)),
                           Image.LANCZOS)
        buf = _io.BytesIO()
        im.convert("RGB").quantize(colors=_FIG_CORES,
                                   method=Image.MEDIANCUT).save(
            buf, "PNG", optimize=True)
        uri = ("data:image/png;base64,"
               + base64.b64encode(buf.getvalue()).decode("ascii"))
    except Exception:
        _FIG_CACHE[chave] = ""
        return None
    _FIG_CACHE[chave] = uri
    return uri


def _digitalizacao_section(rec: CaseRecord, result: CaseResult,
                           figpre: str = "../../variable_explorer/paper_figures/"
                           ) -> str:
    """§3b — CONFERÊNCIA DA DIGITALIZAÇÃO (pedido do professor 2026-07-29):
    o recorte da figura do artigo ao lado da curva que digitalizamos dela, para
    a fidelidade da leitura ser **verificável a olho**, não afirmada.

    O gráfico traz três coisas distintas, que o leitor precisa não confundir:
    a curva **completa** como está no CSV, os pontos que a **métrica** de fato
    comparou (a janela alinhada+trimada), e as convenções de eixo aplicadas
    (`csv_x_scale`/`csv_x_offset`) — sem isso, um x em segundos ou uma âncora
    pré-ciclagem plotada em x=1 parecem erro de digitalização quando são
    convenção declarada."""
    figs = _paper_figs(rec.source, rec.case_id,
                       repo_root() / "New_Theory" / "variable_explorer"
                       / "paper_figures")
    case = rec.validation_case
    # o caminho do CSV vive no RECORD (`csv_path`, absoluto), não no
    # ValidationCase — lá o campo é `reference_csv_path` e nem todos os casos o
    # têm. `load_full_curve` faz `repo_root() / caminho`, e pathlib devolve o
    # absoluto quando o 2º já é absoluto, então passar `rec.csv_path` funciona.
    csv_rel = getattr(rec, "csv_path", None)
    fx = fy = None
    if csv_rel:
        try:
            fx, fy = load_full_curve(csv_rel)
        except Exception:
            fx = fy = None
    mx_ = list(map(float, result.metric_x or []))
    my_ = list(map(float, result.metric_data or []))
    if not figs and fx is None and not mx_:
        return ""
    esc_ = getattr(case, "csv_x_scale", 1.0) or 1.0
    off_ = getattr(case, "csv_x_offset", 0.0) or 0.0
    series = []
    if fx is not None and fy is not None and len(fx):
        series.append(dict(name=f"CSV digitalizado ({len(fx)} pontos)",
                           color="var(--mut)", points=True, line=True,
                           x=[float((v - off_) * esc_) for v in fx],
                           y=list(map(float, fy))))
    if mx_:
        series.append(dict(name=f"pontos que a métrica compara ({len(mx_)})",
                           color="var(--pt)", points=True, line=False,
                           x=mx_, y=my_))
    graf = _chart_div(dict(type="lines", ymax=1.08, h=280, xlabel="ciclos N",
                           ylabel="F/F₀", name=f"{rec.case_id}_digitalizacao",
                           xlog=bool(rec.family == "axial"),
                           series=series)) if series else ""
    figbase = (repo_root() / "New_Theory" / "variable_explorer"
               / "paper_figures")
    # `_fig_data_uri` embute a figura; se falhar (sem Pillow), cai no caminho
    # relativo antigo — degradação, não erro. `loading="lazy"` sai junto com o
    # caminho: não há o que carregar tarde num `data:` URI já presente no HTML.
    def _src(f: str) -> str:
        uri = _fig_data_uri(figbase / f)
        return (f'<img src="{uri}"' if uri
                else f'<img loading="lazy" src="{figpre}{_esc.escape(f)}"')

    imgs = "".join(
        f'<figure class="pfig">{_src(f)}'
        f' alt="figura do artigo — {_esc.escape(rec.source)}">'
        f'<figcaption>{_esc.escape(f)}'
        f'{"" if ok else " — <b>painel não resolvido</b> para este caso: "
                        "confira qual curva da figura corresponde"}'
        f'</figcaption></figure>' for f, ok in figs)
    if not imgs:
        imgs = ('<p class="sub2">Sem recorte da figura no acervo '
                '(<code>variable_explorer/paper_figures/</code>) para esta '
                'fonte — a conferência visual contra o artigo não pode ser '
                'feita aqui, só contra o CSV.</p>')
    notas = []
    if esc_ != 1.0:
        notas.append(f"eixo x do CSV multiplicado por <b>{esc_:g}</b> "
                     f"(convenção da fonte: o artigo publica em outra unidade)")
    if off_:
        notas.append(f"deslocamento de <b>{off_:g}</b> no x "
                     f"(âncora pré-ciclagem plotada fora do zero)")
    if result.align and abs(result.align - 1.0) > 1e-9:
        notas.append(f"o <b>modelo</b> é dividido por {result.align:.4f} antes "
                     f"de comparar (o dado vem normalizado a 1,0 no 1º ponto) — "
                     f"isto NÃO altera o dado desta figura")
    tn = (getattr(result, "config_used", None) or {}).get("trim_n_max")
    if tn:
        notas.append(f"a métrica só pontua N &le; <b>{float(tn):g}</b> (trim "
                     f"registrado) — os pontos além disso estão no CSV mas não "
                     f"entram no erro")
    nota_html = ("<ul class=\"cav\">"
                 + "".join(f"<li>{n}</li>" for n in notas) + "</ul>"
                 ) if notas else ('<p class="sub2">Nenhuma convenção de eixo '
                                  'aplicada: o CSV está em ciclos e F/F₀ '
                                  'diretos.</p>')
    return (f'<h2 id="sec3b">3b. Conferência da digitalização '
            f'<span class="c">— a figura do artigo ao lado do que lemos '
            f'dela</span></h2>'
            f'<div class="grid2"><div>{imgs}</div><div>{graf}</div></div>'
            f'<p class="sub2">Como conferir: a <b>forma</b> da curva cinza tem '
            f'de reproduzir a da figura à esquerda — mesmo joelho, mesmo patamar, '
            f'mesmo final. Os pontos escuros são o subconjunto que o MAE mede; '
            f'onde eles param, o erro para de ser contado. Convenções aplicadas '
            f'a este caso:</p>{nota_html}')


def case_report_html(rec: CaseRecord, result: CaseResult,
                     figpre: str = "../../variable_explorer/paper_figures/",
                     lim_sd: Optional[float] = None) -> str:
    """`figpre` = caminho relativo até `paper_figures/` a partir de ONDE o HTML
    vai ser salvo. O default serve `validation_html/reports/`; o explorador
    salva em `variable_explorer/reports/` e passa `../paper_figures/`. Sem o
    parâmetro, um dos dois teria a imagem quebrada — e quebrada em silêncio,
    porque `<img>` que não carrega não gera erro visível no console.

    `lim_sd` = limite efetivo da 3ª perna desta FONTE (D1, piso por fonte),
    calculado por quem tem o conjunto inteiro (`write_reports`); `None` = o
    global. A página do caso e o documento mestre têm de julgar pela MESMA
    régua — meia-régua em cada lugar foi o defeito de 2026-07-29."""
    case = rec.validation_case
    bc_rows, msd_rows, const_rows = [], [], []
    try:
        inp = inputs_for(case)
    except Exception:
        inp = {}
    try:
        grip = (inp.get("grip_mm", {}) or {}).get("value") or 30.0
        geom = geometry_for_case(case, grip_mm=grip)
    except Exception:
        geom = None
    F0 = case.initial_preload_N
    axial = rec.family == "axial"
    bc_rows += [
        _row("Pré-carga inicial F₀", _fnum(F0 / 1e3, "kN"),
             f"{_fnum(getattr(case, 'preload_percent_yield', None))}% do escoamento"),
        _row("Modo de carga",
             {"axial": "axial (força)", "creep": "creep estático (sem vibração)",
              "transverse": "transversal / disp (Junker)",
              "other": "não parametrizado (modal/força)"}[rec.family]),
        _row("Amplitude transversal", _fnum(case.transverse_displacement_mm, "mm")
             if case.transverse_displacement_mm else "— (sem slip transversal)"),
        _row("Amplitude de força F_amp",
             _fnum((result.config_used or {}).get("F_amp_N"), "N"),
             (inp.get("F_amp_N", {}) or {}).get("prov", "")),
        _row("Frequência", _fnum(case.frequency_Hz, "Hz")),
        # CARGA AXIAL EXTERNA (2026-08-23). Condicao de contorno de TRACAO
        # imposta independentemente do drive transversal — existe no registry
        # desde 53996b7 (as 6 curvas axiais do ECCLES_2010) e NAO era exibida.
        # ⚠️ Input que existe e nao aparece e' da MESMA classe do input que nao
        # existia: as 10 curvas daquela fonte devolviam config identico, e sobre
        # essa sobreposicao foram escritas provas de excecao ("sobreposicao
        # axial"), um bloqueio de pareamento e um "ensemble de 4 replicas".
        # A linha so aparece quando ha carga (isolamento estrutural: quem nao
        # tem axial mantem a tabela byte-identica).
        *([_row("Carga axial externa",
                _fnum(getattr(case, "external_axial_N", 0.0), "N")
                + (f' &middot; {getattr(case, "external_axial_mode", "")}'
                   if getattr(case, "external_axial_mode", "") else ""),
                "paper (nota de aparato; modo constant/intermittent lido)")]
          if float(getattr(case, "external_axial_N", 0.0) or 0.0) > 0.0 else []),
        _row("Ciclos (ensaio)", _fnum(case.n_cycles)),
        _row("Lubrificação", "sim" if getattr(case, "lubricated", False) else "seco"),
        _row("ΔT", "0 (isotérmico)"),
    ]
    msd_rows += [
        _row("Parafuso", f"{case.bolt_size}"),
        _row("Diâmetro nominal / passo",
             f"{_fnum(getattr(case, 'bolt_diameter_mm', None), 'mm')} / "
             f"{_fnum(getattr(case, 'pitch_mm', None), 'mm')}"),
    ]
    if geom is not None:
        msd_rows += [
            _row("Diâmetro de passo d₂", _fnum(geom.d_2 * 1e3, "mm")),
            _row("Área de tensão A_s", _fnum(geom.A_s * 1e6, "mm²")),
            _row("Comprimento efetivo L_eff (grip)", _fnum(geom.L_eff * 1e3, "mm"),
                 (inp.get("grip_mm", {}) or {}).get("prov", "")),
            _row("Rigidez do parafuso k_b", _fnum(geom.k_b / 1e6, "MN/m"),
                 "E·A_s/L_eff"),
            _row("Raio de apoio r_bearing / área A_contact",
                 f"{_fnum(geom.r_bearing*1e3, 'mm')} / {_fnum(geom.A_contact*1e6, 'mm²')}",
                 "anel real π(r_b²−r_furo²), §4.9-11g"),
        ]
    msd_rows += [
        _row("Atrito µ (rosca=apoio)", _fnum((inp.get("mu", {}) or {}).get("value")),
             (inp.get("mu", {}) or {}).get("prov", "")),
        _row("Rugosidade Rz", _fnum((inp.get("rz", {}) or {}).get("value")),
             (inp.get("rz", {}) or {}).get("prov", "")),
    ]
    # constantes: config per-rig adotada + shared
    adopted = None
    for s in kb.adopted_sources():
        if rec.source.split("_")[0].upper() in s.upper():
            adopted = kb.adopted_config(s)
            break
    cfg = (adopted or {}).get("cfg", {}) if adopted else {}

    def _walk(d):
        for k, v in d.items():
            if isinstance(v, dict):
                _walk(v)
            elif isinstance(v, (int, float, str, bool)):
                const_rows.append(_row(k, _fnum(v),
                                       PROV.get(k, "config adotada per-rig")))
    _walk(cfg)
    try:
        for k, v in load_shared_material().items():
            const_rows.append(_row(k, _fnum(v),
                                   SHARED_PROV.get(k, "Estágio A compartilhada")))
    except Exception:
        pass
    verdict = (adopted or {}).get("verdict", "") if adopted else ""

    # resultado / degradacao
    if not result.ok:
        result_html = (f'<h2 id="sec3">3. Resultado e erro</h2><p class="verd">'
                       f'Não simulável (degradação honesta): {result.error}</p>')
    else:
        dx, dy = _data_points(rec)
        mx = np.asarray(result.cycles, dtype=float)
        my_raw = np.asarray(result.ratio, dtype=float)
        # A metrica do runner compara o modelo ALINHADO (dividido pelo proprio
        # valor no 1o ciclo do dado) e SO dentro da janela de trim. Ate 2026-07-27
        # esta pagina plotava/recomputava sobre a curva CRUA e SEM trim, entao
        # cabecalho, grafico, residuo e MAE-por-estagio eram quatro numeros
        # diferentes (li2022ti full: 0.0317 no topo vs 0.19/0.30/0.28 nos
        # estagios). Aqui reproduzimos exatamente a convencao da metrica.
        align = float(result.align) if result.align else 1.0
        my = my_raw / align
        trim_n = (result.config_used or {}).get("trim_n_max")
        trim_n = float(trim_n) if isinstance(trim_n, (int, float)) else None
        # Pontos que a METRICA de fato comparou. Preferimos SEMPRE os vetores
        # gravados pelo runner (grade completa); o recorte por trim aqui embaixo
        # e' so fallback p/ registros de store anteriores a 2026-07-27, e ainda
        # herda o erro de reinterpolar na grade amostrada.
        dx_m = np.asarray(result.metric_x, dtype=float)
        dy_m = np.asarray(result.metric_data, dtype=float)
        pred_m = np.asarray(result.metric_pred, dtype=float)
        if not len(dx_m):
            dx_m, dy_m = np.asarray(dx, dtype=float), np.asarray(dy, dtype=float)
            if trim_n is not None and len(dx_m):
                keep = dx_m <= trim_n
                dx_m, dy_m = dx_m[keep], dy_m[keep]
            pred_m = (np.interp(dx_m, mx, my) if len(dx_m) and len(mx)
                      else np.asarray([], dtype=float))
        banners = []
        if rec.case_class == "final_ratio":
            banners.append(
                f'<p class="verd">Sem curva digitalizada — comparação pontual: '
                f'ratio final esperado {_fnum(result.final_data)} vs previsto '
                f'{_fnum(result.final_pred)}.</p>')
        mae_html = (f'<div class="metric '
                    f'{"good" if (result.mae or 1) <= META_MAE else "warn"}">'
                    f'MAE {result.mae:.4f}</div>'
                    if result.mae is not None else
                    '<div class="metric warn">MAE —</div>')
        camp = ""
        if rec.gallery_entry is not None and result.engine_fingerprint != "gallery-seed":
            g = float(rec.gallery_entry["mae"])
            camp = (f' &#183; campanha {g:.4f} (melhor config experimental — '
                    f'divergência = gap de adoção)')
        sub = (f'<div class="sub2">erro máx {_fnum(result.maxerr)} @ ciclo '
               f'{_fnum(result.maxerr_at)}{camp}</div>')
        # `n_total` = pontos do dado CRU, para a linha de cobertura da métrica.
        # Lê pelo mesmo caminho que o runner (offset/scale aplicados), e degrada
        # para None em silêncio: a linha simplesmente não aparece, nunca quebra a
        # página por causa de uma CSV ilegível.
        n_total = None
        try:
            from .inputs import load_full_curve
            _cyc, _rat = load_full_curve(str(rec.csv_path))
            n_total = len(_rat)
        except Exception:
            pass
        tripe_html = _tripe_block(result, lim_sd, n_total)
        # ESTATUTO NA PÁGINA POR CASO (2026-08-21, investigação do chu test2
        # a pedido do professor): a página mostrava o cartão vermelho SEM
        # dizer que a curva é exceção assinada/declarada — o estatuto vivia
        # só no documento mestre, e quem abria o report por caso via uma
        # reprovação sem contexto. Mesma classe do defeito que o
        # _tripe_block consertou (§3): a página por caso contradizia o
        # documento mestre em silêncio.
        _rotulo_est = _sub_est = _prova_est = None
        if rec.case_id in _EXCECOES:
            _rotulo_est = "EXCEÇÃO ASSINADA (F5/F7)"
            _sub_est = ("fora do tripé e COBERTA no documento mestre — "
                        "exceção retira da meta, não fecha a curva")
            _prova_est = str(_EXCECOES[rec.case_id] or "")
        elif rec.case_id in _DECLARADAS:
            _rotulo_est = "DECLARADA"
            _sub_est = ("fora do tripé e fora da FILA DE TRABALHO por "
                        "critério medido — declarada ≠ acerto do modelo")
            _prova_est = str(_DECLARADAS[rec.case_id] or "")
        if _prova_est is not None:
            tripe_html += (
                '<div style="border-left:4px solid #b58900;padding:8px 12px;'
                'margin:10px 0;opacity:.92">'
                f'<b>{_rotulo_est}</b> &#8212; {_esc.escape(_sub_est or "")}.<br>'
                f'<span class="sub2">prova/motivo: {_esc.escape(_prova_est)}'
                '</span></div>')
        # erro dedicado: narrativa + residuo assinado + MAE por estagio
        stage_html = ""
        residual_html = ""
        if len(dx_m) and len(pred_m) and result.mae is not None:
            stages = _stage_maes(dx_m, dy_m, pred_m)
            # O alvo do MAE por estágio é o MESMO `META_MAE` da perna do tripé —
            # é um MAE. Estava fixo em 0.1 (a régua de DUAS pernas, anterior a
            # 2026-07-29): o estágio dizia "no alvo" com 0.08 enquanto a curva
            # reprovava no documento mestre pelo mesmo número.
            stage_rows = "".join(
                _row(f"Estágio {k} ({rng})", _fnum(v),
                     "" if v is None else ("no alvo" if v <= META_MAE
                                           else f"acima do alvo {META_MAE:.4g}"))
                for (k, rng), v in zip((("I", "0-10% ciclos, assentamento"),
                                        ("II", "10-70%, perda principal"),
                                        ("III", "70-100%, cauda")),
                                       stages.values()))
            stage_html = (f'<h3>Erro por estágio</h3><table>{stage_rows}</table>')
            resid = (pred_m - dy_m).tolist()
            residual_html = (
                f'<h3>Resíduo assinado (modelo &#8722; artigo)</h3>'
                + _chart_div(dict(
                    type="lines", sym=True, band=float(result.mae), h=190,
                    xlabel="ciclos N", ylabel="resíduo F/F₀",
                    name=f"{rec.case_id}_residuo", xlog=bool(axial),
                    series=[dict(name="resíduo (modelo − dado)",
                                 color="var(--err)", points=True, line=True,
                                 x=list(map(float, dx)), y=resid)]),
                    "residual")
                + '<p class="sub2">acima de zero = modelo sobre-prediz '
                  'F/F&#8320; (afrouxa mais devagar que o artigo) &#183; '
                  'abaixo = sub-prediz &#183; faixa sombreada = &#177;MAE</p>')
        main_series = []
        if len(dx):
            main_series.append(dict(name="dado (artigo)", color="var(--pt)",
                                    points=True,
                                    x=list(map(float, dx)),
                                    y=list(map(float, dy))))
        if len(mx):
            ax_, ay_, _ = _aligned_model_xy(result, mx, my_raw)
            if align != 1.0:
                main_series.append(dict(
                    name=f"modelo cru (antes do alinhamento ÷{align:.4f})",
                    color="var(--mut)", dash=True,
                    x=list(map(float, mx)), y=list(map(float, my_raw))))
            main_series.insert(1 if len(dx) else 0,
                               dict(name="modelo (alinhado = o que o MAE mede)"
                                    if align != 1.0 else "modelo",
                                    color="var(--di)", x=ax_, y=ay_))
        main_chart = _chart_div(dict(
            type="lines", ymax=1.08, h=300, xlabel="ciclos N",
            ylabel="F/F₀", name=f"{rec.case_id}_curva",
            xlog=bool(axial), vline=trim_n, series=main_series))
        result_html = (f'<h2 id="sec3">3. Resultado e erro</h2>'
                       f'{"".join(banners)}{mae_html}{sub}{tripe_html}'
                       f'{_metric_window_note(align, trim_n, dx, dy)}'
                       f'{_error_narrative(result, dx_m, dy_m, pred_m)}'
                       f'{main_chart}{residual_html}{stage_html}')

    items = "".join(f"<li>{c}</li>" for c in rec.caveats)
    # F1 item 2 (prereg 2026-07-21): check L7 informacional default-on — so'
    # renderiza quando houve remocao de material (implied != None); fora da
    # banda = sinal de par nao-casado mu x k_wear (report L1-L7 §3.5), nunca
    # erro de simulacao.
    trim_n = (getattr(result, "config_used", None) or {}).get("trim_n_max")
    trim_html = ""
    if trim_n:
        trim_html = (f'<p class="sub2"><b>Trim registrado</b> (exce&#231;&#227;o '
                     f'bloco C, prereg F3): m&#233;trica computada s&#243; em '
                     f'N &#8804; {trim_n:g} &#8212; trecho posterior &#233; '
                     f'out-of-model (fratura/terminal); curva completa segue '
                     f'no plot. Lista de exce&#231;&#245;es assina na F5.</p>')
    l7 = getattr(result, "l7_check", None) or {}
    l7_html = ""
    if l7.get("implied_J_per_mm3") is not None:
        b = l7.get("bound") or {}
        dentro = bool(l7.get("in_bound"))
        estado = ("dentro da banda" if dentro else
                  "<b>FORA DA BANDA</b> &#8212; sinal de par n&#227;o-casado "
                  "&#181;&#215;k_wear (usar pares casados por interface; "
                  "informacional, n&#227;o &#233; bug)")
        l7_html = (f'<p class="sub2">Check L7 (energia espec&#237;fica de '
                   f'remo&#231;&#227;o): implied '
                   f'{l7["implied_J_per_mm3"]:.3g} J/mm&#179; &#8212; {estado} '
                   f'[{b.get("lo", 0):.3g}, {b.get("hi", 0):.3g}] '
                   f'({b.get("source", "")})</p>')
    note = ""
    if rec.apparatus_note_path is not None:
        rel_note = rec.apparatus_note_path.relative_to(repo_root()).as_posix()
        note = (f'<p class="sub2">Nota de aparato: '
                f'<a href="../../../{rel_note}">{rec.apparatus_note_path.name}</a></p>')
    verd = f'<p class="verd">{verdict}</p>' if verdict else ""
    body = ((f"<ul>{items}</ul>" if items else "") + trim_html + l7_html
            + note + verd) or \
        '<p class="sub2">Sem caveats registrados para este caso.</p>'
    caveats_html = f'<h2 id="sec6">6. Caveats e veredicto</h2>{body}'

    doi = getattr(case, "doi", None)
    url = getattr(case, "url", None)
    src_link = (f'<a href="https://doi.org/{doi}">{doi}</a>' if doi
                else (f'<a href="{url}">fonte</a>' if url else ""))
    mae_badge = (f'<span class="chip">MAE <b>{result.mae:.4f}</b></span>'
                 if (result.ok and result.mae is not None) else "")
    # RESUMO EXECUTIVO no topo — a 1ª coisa que se lê. Estava na régua de DUAS
    # pernas ("no alvo (<=0.1)"), então uma curva reprovada no documento mestre
    # abria a própria página anunciando-se no alvo. Agora dá o veredicto das TRÊS
    # e nomeia a perna que manda.
    if result.ok and result.mae is not None and result.maxerr is not None:
        _eff = META_SRES if lim_sd is None else float(lim_sd)   # D1
        _p = _perna_manda(result.mae, result.maxerr,
                          getattr(result, "resid_std", None),
                          META_MAE, META_MAX, _eff)
        _sev = _severidade(result.mae, result.maxerr,
                           getattr(result, "resid_std", None),
                           META_MAE, META_MAX, _eff)
        _NM = {"mae": "o MAE", "mx": "o resíduo máximo", "sd": "o σ_res"}
        resumo = (
            f'<span class="metric {"good" if _p is None else "warn"}">'
            f'MAE {result.mae:.3f}</span> — '
            + ('<b>passa nas três pernas</b> do tripé '
               f'(MAE &#8804;{META_MAE:.4g} · res.máx &#8804;{META_MAX:.4g} · '
               f'σ_res &#8804;{META_SRES:.4g})' if _p is None else
               f'<b>fora do tripé</b>: {_sev:.2f}× o limite na perna que manda, '
               f'que é <b>{_NM[_p]}</b> (detalhe perna por perna na §3)'))
    elif not result.ok:
        resumo = ('<span class="metric warn">não simulável</span> — '
                  + (result.error or ''))
    else:
        resumo = ('<span class="metric warn">sem curva</span> — comparação '
                  'pontual do ratio final')
    toc = ('<nav class="toc"><b>Índice</b>'
           '<a href="#sec1">1. Condições de contorno</a>'
           '<a href="#sec2">2. Modelo MSD</a>'
           '<a href="#sec3">3. Resultado e erro</a>'
           '<a href="#sec4">4. Decomposição</a>'
           '<a href="#sec5">5. Constantes</a>'
           '<a href="#sec6">6. Caveats</a>'
           '<a href="#top">&#8593; topo</a></nav>')
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{rec.case_id} — report de validação</title>{_CSS}</head><body>
{_topbar(rec.case_id, mae_badge)}{toc}<div class="wrap">
<noscript><p class="verd">Gráficos interativos requerem JavaScript — os dados
e tabelas do report seguem legíveis sem ele.</p></noscript>
<p class="back"><a href="../validation_report.html">&#8592; casos de validação</a></p>
<h1 id="top">{rec.case_id}</h1>
<p class="sub">{NICE.get(rec.source, rec.source)} &#183; {_FAM_PT[rec.family]} &#183;
 {_CLASS_PT[rec.case_class]} &#183; {src_link}</p>
<p class="exec">{resumo}</p>
<div class="grid2">
  <div>
    <h2 id="sec1">1. Condições de contorno</h2><table>{"".join(bc_rows)}</table>
  </div>
  <div>
    {result_html}
  </div>
</div>
{_digitalizacao_section(rec, result, figpre)}
{_msd_section(rec, geom_rows="".join(msd_rows))}
{_decomp_section(result)}
<h2 id="sec5">5. Constantes usadas (com proveniência)</h2>
<table class="wide">{"".join(const_rows)}</table>
{caveats_html}
<p class="foot">Gerado em {result.generated_at} &#183; engine
 {result.engine_fingerprint} &#183; bolt_analysis_studio.validation (Plano A).
 Veredictos de física: MODEL_LEGITIMACY.md &#183; referência do modelo:
 MODEL_MATH_REFERENCE.md.</p>
</div>{_CHART_JS}{_PAGE_JS}</body></html>'''


def _budget_path():
    return (repo_root() / "Models" / "CALIBRATION_AND_VALIDATION"
            / "error_budget.json")


_BUDGET_LABELS = ("no_piso", "gap_adocao", "nivel", "forma", "sem_simulacao")

# META da campanha: TRIPÉ POR CURVA. Um único lugar define os limiares; chips,
# vereditos, filtros e os painéis leem daqui.
#
# TRIPÉ DE TRÊS PERNAS (decisão do professor, 2026-07-29):
#   res.máx <= 0.10  ·  MAE <= 0.05  ·  σ_res <= 0.025
# Antes eram duas pernas (MAE <= 0.10 E maxerr <= 0.10). Cada valor tem âncora
# medida ou normativa — derivação completa e reprodutível em
# `New_Theory/piso_repetibilidade_medido.md`, e resumida na própria página pela
# seção "Por que estes limites" (que RECOMPUTA os pisos do store na geração, de
# modo que o número exibido não pode divergir do dado):
#   · res.máx 0.10  = 25% acima do piso mediano medido (0.0795) e 2x a margem
#                     de decisão normativa. É a única perna que já era ancorada.
#   · MAE 0.05      = a MARGEM DE DECISÃO das normas: ISO 16130:2015 põe a zona
#                     "boa" em 85% e a DIN 25201-4 aprova em 80% ⇒ a decisão de
#                     engenharia mora numa faixa de 0.05 em F/F₀. Um erro médio
#                     menor que ela não inverte veredicto de norma. Fica ~17%
#                     ABAIXO do piso mediano (0.060): escolha de ambição, feita
#                     com o custo na mesa (59 curvas de fontes cujo piso já
#                     viola o limite).
#   · σ_res 0.025   = a MEDIANA do piso de repetibilidade medido (0.0241) em 19
#                     famílias de réplica / 16 fontes, arredondada para cima. É
#                     5x o piso de digitalização declarado (±0.005, Liu 2017),
#                     logo mensurável, e não pede ao modelo fidelidade que o
#                     experimento não tem consigo mesmo.
# Impacto medido no store `3546e6745448` ANTES de instalar (mudança de régua
# muda o número-manchete, então a conta vem primeiro):
#   149 (2 pernas) -> 105 com estes limites. A 1ª proposta do dia era
#   σ_res <= 0.010 e dava 45 — foi revista porque 107 das 203 curvas pertencem a
#   fontes cujo piso de σ JÁ viola 0.010, isto é, a maioria das reprovações não
#   mediria o modelo, mediria o dado.
META_MAX = 0.10      # resíduo máximo — maior desvio pontual |modelo − dado|
META_MAE = 0.05      # erro médio absoluto ao longo da curva
META_SRES = 0.025    # desvio-padrão do resíduo assinado (perna nova)
N_MIN_SRES = 6       # n mínimo p/ julgar a 3ª perna (assinado 2026-08-01:
                     # n<6 ⇒ não-julgável ⇒ fora do tripé + declarada;
                     # prereg 2026-08-01-n-minimo-sres-prereg.md)
# rótulo do estatuto no `<title>`/leitor de foco do 3D — a FORMA diz que o
# ponto é diferente, o TEXTO diz o que ele é (forma sozinha exige legenda)
_ROT_ESTATUTO = {"exc": " — EXCEÇÃO assinada (◆)",
                 "decl": " — DECLARADA (■)"}
# Piso de digitalização DECLARADO na literatura (Liu 2017: ±0.005 em F/F₀,
# resolução de 5%/divisão). Nada abaixo disto é mensurável na figura; serve de
# referência inferior no eixo do σ_res.
_PISO_DIGITALIZACAO = 0.005
# Alias de compatibilidade: onde só cabe UM número (a linha do ledger, o teto
# dos eixos do 3D, a régua do orçamento) vale a do res.máx, que é a perna que
# não mudou.
META = META_MAX
# Ponto de partida da execução mestre (ledger F0.4, 2026-07-21: 99 violadores
# em 202 comparáveis => 103 no tripé). Usado só na barra de progresso.
_PARTIDA_TRIPE = 103
# Fonte dos casos que NÃO entram no censo de comparáveis (casos do usuário e
# exemplos sintéticos aparecem no documento, mas não na meta).
# UFU_LAB: FORA DO PROJETO (decisão do professor em 2026-08-01 — primeiro
# "por enquanto", depois DEFINITIVA na mesma data: *"a UFU não faz parte mais
# desse projeto"*). Os 3 ensaios da bancada própria não entram na meta e não
# há rodada experimental pendente — o item saiu da fila de decisões. Nada foi
# apagado: resultados, CSVs, configs e reports ficam PRESERVADOS no
# store/repositório (reverter = tirar a string desta tupla e re-sincronizar
# censo/docs no mesmo commit).
_SRC_NAO_COMPARAVEL = ("USER", "UFU_LAB")
# CASOS individuais fora do censo (P2 do plano LU_2024, decisão do professor
# 2026-07-31): a linha 22 N·m da Tabela 9 do paper é IDÊNTICA ao dígito à
# linha 1,0 mm da Tabela 8 — fig18_amp1p0 e fig20_T22Nm são o MESMO teste
# publicado em duas figuras. Contar os dois é contar a mesma medição 2×.
# Mantida a T22 (F₀ da Tabela); a amp1p0 fica no STORE (o par é o piso de
# digitalização da fonte) mas fora de censo/meta/fila.
_CID_NAO_COMPARAVEL = {
    "lu2024_M8_fig18_amp1p0":
        "duplicata de lu2024_M8_fig20_T22Nm (mesmo teste em 2 figuras; "
        "Tabela 8@1,0mm ≡ Tabela 9@22N·m; P2, professor 2026-07-31)",
}


# PARES DE RÉPLICA DECLARADOS (prereg 2026-07-31-pares-replica-declarados):
# réplicas de condição nominal repetida cujo F0 ALCANÇADO difere — o aperto
# nunca repete (4–14 % nos pares do LU) — e que a chave mecânica de
# `_pisos_medidos` nunca casaria. Cada par carrega a proveniência.
_PARES_REPLICA_DECLARADOS = [
    # CACCESE: o ÚNICO par verdadeiro da fonte (mesma condição, "rep1"/"rep2"
    # no próprio nome). Entra declarado porque o bloqueio da chave cega
    # (prereg 2026-08-01-familias-falsas) tirou as 7 curvas do pareamento
    # automático — sem esta linha o piso legítimo desta condição sumiria.
    ("caccese2009_tapered_45kN_rep1", "caccese2009_tapered_45kN_rep2",
     "tapered 45 kN — réplicas rep1/rep2 da MESMA condição"),
    # ECCLES_2010 (item O, prereg 2026-08-15-eccles-par-replica-declarado,
    # assinado pelo professor às 19:14). O bloqueio da fonte
    # ("carga axial ≠ — é a variável varrida") está CERTO para os 6 pares que
    # cruzam cargas axiais; ele é apenas LARGO DEMAIS, porque as 4 curvas
    # `no_axial` têm carga axial ZERO e não diferem na variável varrida.
    # Declara-se UM par, cirurgicamente — desbloquear a fonte reabriria os 6
    # pares inválidos que a P-15 justamente fechou.
    # PROCEDÊNCIA: o rótulo é DO AUTOR. O paper nomeia as duas curvas
    # `baseline1` e `baseline2` da mesma condição sem carga axial — o mesmo
    # estatuto de `rep1/rep2` (CACCESE) e `run1/run2` (LIU_2016).
    # ⚠️ POR QUE NÃO OUTRO DOS 6 PARES `no_axial`: eles dão TRÊS vereditos
    # diferentes (medido, `item_O_nao_executar_o_veredito_depende_do_par.md`).
    # `fig3_typical` é curva ILUSTRATIVA e `fig7a` é baseline de OUTRA série;
    # pareá-las é afirmação mais fraca que a do autor. Foi por citar a faixa
    # dos pares fracos (piso 0,1134) que o item O quase retratou 2 exceções
    # que o piso CORRETO sustenta — 7ª questão de validade de piso da campanha
    # e a 1ª em sentido DEFENSIVO.
    ("eccles2010_fig8a_no_axial_baseline1",
     "eccles2010_fig8c_no_axial_baseline2",
     "no axial — baseline1/baseline2 da MESMA condição, rótulo DO AUTOR "
     "(Fig. 8a × 8c)"),
    # ⛔ Os 3 pares §3.1.3×Fig.18/20 do LU_2024 foram REMOVIDOS em 2026-08-14:
    # NÃO são réplicas — o PRÓPRIO PAPER separa os protocolos. As corridas
    # longas são a §3.1.3 (half-sine, controle de MÁQUINA, 1 Hz; F0 iniciais
    # 12.398/12.285/12.696 N, p.14) e as Fig.18/20 são a §3.2, cujo texto abre
    # dizendo que o controle MANUAL de estica-comprime "elimina os efeitos da
    # half-sine" (p.15). Medido (commit 9784148): tempo até 0,90·F0 difere
    # 27–56×, plateau SEMPRE do lado da §3.1.3, 3/3 pares — sistemático entre
    # figuras = diferença de PROTOCOLO, não do ensaio; e coerente com o achado
    # de frequência do próprio Lu (§3.1.2: frequência menor ⇒ MUITO mais
    # afrouxamento por ciclo — ciclo manual ≈ frequência ultrabaixa).
    # 4ª invalidação de pareamento da campanha; regra: VALIDADE DO PAR VEM
    # ANTES DO NÚMERO. Consequências em _EXCECOES_RETRATADAS_LU_PROTOCOLO.
    # LI_2022_TRIBOINT (2026-08-05): o único par de MESMA condição da fonte,
    # preservado ao bloquear a chave cega à frequência. É piso de
    # **repetibilidade entre ESPÉCIMES** (σ 0,0083), e isso foi MEDIDO, não
    # suposto — a hipótese "mesmo ensaio em 2 figuras" (que mudaria o
    # DENOMINADOR via `_CID_NAO_COMPARAVEL`) foi **falsificada**
    # (`fila_form_limited_3_anatomia.md` §3): nenhuma atribuição de base faz as
    # trajetórias ABSOLUTAS coincidirem — o fator de escala ótimo B→A é 1,0234
    # e não 1,0435 (=12,0/11,5), e sobram 0,112 kN de FORMA depois de escalar.
    # A convergência 4,2 %→0,5 % é monótona: assinatura de dois F₀ distintos sob
    # a MESMA carga imposta (modo força), não de erro de digitalização. E a
    # Fig. 12 plota 3 espécimes a 10 Hz (vidas 2,87/3,58/4,16 ×10⁵).
    ("li2022ti_axialmin_10Hz", "li2022ti_axial_10Hz_full",
     "10 Hz — Fig. 8c × Fig. 8a, mesma condição, ESPÉCIMES distintos"),
    # LIU_2016 (2026-08-06): o único par de réplica VERDADEIRO da fonte — o
    # próprio paper: "the self-loosening curves of two bolted joints ... are
    # different under the same working condition" (Fig. 7, p.68). Preservado ao
    # bloquear a família falsa. ⚠️ CAVEAT medido (sonda de pixel 2026-08-06):
    # os IMPRESSOS de run1/run2 divergem ~1,78 pt em média, os CSVs só 0,44 —
    # com OVERPRINT em 200k–500k (a run2 cobre os glifos da run1) ⇒ o piso de
    # CSV pode SUBESTIMAR o scatter real. Seguro nas duas direções: o `max`
    # de `limite_sres` nunca aperta, e piso baixo só DIFICULTA prova F7.
    ("liu2016wear_fig7_run1_1e6cyc", "liu2016wear_fig7_run2_5e6cyc",
     "Fig. 7 — run1/run2, mesma condição (piso pode subestimar: overprint)"),
    # KARLSEN_2022 (D-Y, 2026-08-06): este par SUSTENTA o piso da fonte inteira
    # e a correção de base da `run2.2` o desfaria. Até hoje as duas casavam
    # pela chave mecânica porque **ambas** carregavam F₀ = 312 kN — o valor
    # NOMINAL. Medida a Fig. 10, a `run2.2` alcançou ~333 kN (a `run7.1` ficou
    # em 313, +0,4 % do nominal), então o F_amp deixa de coincidir e a chave
    # para de pareá-las. São réplicas legítimas: MESMO sistema (HV tensionada
    # M30), MESMA condição nominal, espécimes diferentes — e é justamente o
    # scatter entre elas (vidas 195/230/340 no paper) que o piso mede.
    # ⚠️ Declarar aqui é MAIS honesto que o estado anterior, onde o par era
    # mantido por um F₀ nominal que sabemos errado numa das duas. Sem isto,
    # `limite_sres(KARLSEN)` cairia de 0,0845 ao global 0,025 e QUATRO curvas
    # reprovariam por σ (`run6p2` 0,0300 · `run7p1` 0,0504 · `M42_run21p0`
    # 0,0337 · a própria `run2p2`) — perda causada pela correção, não medida.
    ("karlsen2022_M30_HV_run2p2", "karlsen2022_M30_HV_run7p1",
     "HV M30 tensionada — mesma condição nominal, F₀ alcançado 333 × 313 kN"),
]


def caso_comparavel(source: str, case_id: str) -> bool:
    """Filtro ÚNICO do censo de comparáveis — todo consumidor passa por aqui
    (report, triagem, testes) para fonte E caso ficarem em um só lugar."""
    return (source not in _SRC_NAO_COMPARAVEL
            and case_id not in _CID_NAO_COMPARAVEL)


# FONTES RETIRADAS DO DOCUMENTO (decisão do professor, 2026-07-31): não são
# mais usadas para validar o software, então não aparecem — nem em linha, nem em
# gráfico, nem em contagem.
#
# ⚠️ Este filtro NÃO é o mesmo que `_SRC_NAO_COMPARAVEL`, e a diferença é o
# ponto todo:
#   · `_SRC_NAO_COMPARAVEL` = **aparece no documento, fora do censo**. É o caso
#     do `USER` (`exemplo_m12_sintetico`): é útil ver, não é evidência de
#     validação. Sair do censo é uma afirmação sobre a MÉTRICA.
#   · `_SRC_RETIRADO` = **não aparece**. É uma afirmação sobre o CORPUS: aquela
#     fonte deixou de ser prova. Mostrá-la faria o leitor contar como evidência
#     algo que o autor já retirou.
# UFU_LAB já havia saído do censo em `f8eb930` ("por enquanto"); a retirada do
# documento é a decisão seguinte e definitiva, e por isso vive numa lista
# própria — devolver a fonte ao censo não deve, sozinho, devolvê-la à página.
_SRC_RETIRADO = {
    "UFU_LAB": "bancada do próprio laboratório; não é mais usada para validar "
               "o software (professor, 2026-07-31)",
}


def caso_no_documento(source: str, case_id: str) -> bool:
    """Este caso deve ser DESENHADO no documento mestre?

    Filtro de presença, anterior ao de censo. Todo gerador (mestre, galeria de
    gráficos) passa por aqui, para que retirar uma fonte seja uma edição em um
    lugar só e não uma caça a tabelas."""
    return source not in _SRC_RETIRADO


def _nota_retirados(retirados) -> str:
    """Nota de rodapé nomeando o que foi retirado do documento, e por quê.

    Retirar em SILÊNCIO seria apagar. Um leitor que conheça o corpus vai
    procurar a fonte; sem esta nota ele concluiria que ela nunca existiu, ou
    que passou. Os casos continuam no store e no registry — o que mudou é o
    estatuto de prova, e é isso que a nota diz."""
    if not retirados:
        return ""
    por_fonte: Dict[str, int] = {}
    for r in retirados:
        por_fonte[r.source] = 1 + por_fonte.get(r.source, 0)
    itens = " &#183; ".join(
        f'<b>{_esc.escape(NICE.get(s, s))}</b> ({n} '
        f'{"caso" if n == 1 else "casos"}) — '
        f'{_esc.escape(_SRC_RETIRADO.get(s, ""))}'
        for s, n in sorted(por_fonte.items()))
    return (f'<p class="foot"><b>Fontes retiradas deste documento:</b> {itens}. '
            f'Não entram em nenhuma tabela, gráfico ou contagem desta página. '
            f'Os registros seguem no <code>validation_store</code> e no '
            f'registry — o que mudou é o <b>estatuto de prova</b>, não o dado: '
            f'nada foi apagado, e a decisão é reversível tirando a fonte de '
            f'<code>_SRC_RETIRADO</code>.</p>')

# EXCEÇÕES ASSINADAS. Dois documentos, um dicionário de leitura:
#   · `_F5_EXCECOES` — F5 (`New_Theory/f5_excecoes_propostas.md`), **assinada em
#     2026-07-28** (S4, 8/8). O comentário anterior dizia "PROPOSTAS, NÃO
#     ASSINADAS" e ficou vencido no dia seguinte à assinatura.
#   · `_F7_EXCECOES` — F7 por PROVA DE PISO
#     (`New_Theory/f7_excecoes_por_prova_de_piso.md`), **assinada em 2026-07-29**.
# Consumidores leem `_EXCECOES` (a UNIÃO). Isso não é estilo: 9 curvas estão nos
# DOIS documentos, e somar as listas daria 54 onde são 45 — a chave do dict
# impede a dupla contagem por construção. Ao editar, edite no MESMO commit que o
# documento correspondente. Marcadas aqui para que a
# linha vermelha diga POR QUE está vermelha. Os TRIMS (LIU_2025 x7,
# YANG_2021 x6, li2022ti full, SECOS x2) não entram nesta tabela: já aparecem
# pelo badge de trim, lido de config_used.trim_n_max.
# SINCRONIZADO com a revisão 2026-07-27 do documento (censo certificado S3).
# Ao editar a lista de exceções, edite este dict no MESMO commit: ele dirige o
# badge §F5, o filtro "excecao" e a contagem do painel — divergir daqui faz o
# report mestre mostrar um conjunto e a assinatura outro.
_F5_EXCECOES = {
    # §A scatter de réplicas — desvios-à-mediana re-medidos em 2026-07-27 dos
    # CSVs pelo leitor canônico (fig6 0.328 @N=150; fig8 0.349 @N=835).
    # Trio conferível acrescentado em 2026-08-21 (medição do tick 14:55):
    # pisos = MEDIANAS par-a-par das 6 réplicas (15 pares, janela da métrica
    # y>=0,10, interpolação na janela comum, grid 60) — mx 0,2611 · MAE 0,1124
    # · σ 0,0916. O modelo vs cada réplica erra MENOS que as réplicas entre si
    # em quase toda perna (rep4 σ é a única a 1,02x do piso). A rota de fechar
    # por floor foi FALSIFICADA no dado cru no mesmo tick: as 6 colapsam a
    # 0,03-0,065 (o "arresto em 0,14-0,19" era o FLOOR_TRIM no metric_data —
    # 3ª instância da armadilha documentada); o floor adotado 0,05 está certo.
    "bauer2024_M8_fig6_rep1": "scatter de réplicas (desvio-à-mediana 0.328): "
        "res.máx 0.1259/0.2611 · MAE 0.0431/0.1124 · σ 0.0430/0.0916",
    # rep4: o σ fica FORA do formato-trio de propósito (guarda
    # test_a_prova_ainda_e_verdadeira lê "v/p" como claim v<=p): σ 0,0932
    # está 1,7% ACIMA do piso par-a-par 0,0916 — a perna σ NÃO é coberta
    # por prova de piso; a exceção sustenta-se na F5 (desvio-à-mediana),
    # e as 2 pernas restantes têm o trio conferível.
    "bauer2024_M8_fig6_rep4": "scatter de réplicas (desvio-à-mediana 0.328): "
        "res.máx 0.1709/0.2611 · MAE 0.0783/0.1124; sigma 0.0932 fica 1,7% "
        "acima do piso par-a-par (0.0916) — perna coberta pela F5, não por "
        "prova de piso",
    "bauer2024_M8_fig6_rep5": "scatter de réplicas (desvio-à-mediana 0.328): "
        "res.máx 0.1116/0.2611 · MAE 0.0494/0.1124 · σ 0.0586/0.0916",
    "bauer2024_M8_fig6_rep6": "scatter de réplicas (desvio-à-mediana 0.328): "
        "res.máx 0.1300/0.2611 · MAE 0.0757/0.1124 · σ 0.0464/0.0916",
    # RETRATADA em 2026-08-07 — **P-11 ASSINADA**. Ver
    # _EXCECOES_RETRATADAS_P11: res.máx 0,3965 contra o próprio
    # desvio-à-mediana 0,349 (1,14×).
    # test2 RETIRADA em 2026-08-20 — fechou POR MÉRITO com o limiar do
    # espectro por espécime (prereg bauer-fig8-scrit-especime); prova em
    # _EXCECOES_RETIRADAS_BAUER_SCRIT.
    "bauer2024_M12_fig8_test3": "scatter de réplicas (desvio-à-mediana 0.349)",
    # §E CHU_2026 — form-limited com prova em NÍVEL DE LEI, em 5 degraus
    # (ASSINADA por delegação em 2026-08-14, "assine e continue em loop";
    # dossiê: prereg 2026-08-13-chu2026-calibracao + chu2026_estudo.md §7-9):
    # (1) µ-livre não reproduz; (2) µ(N) MEDIDO prescrito ≈ inerte (canal
    # Archard é cego a µ); (3) lei de wear µ-acoplada morre na âncora;
    # (4) 4 famílias estado-dirigidas falsificadas em grade (k_wear uniforme,
    # running-in, ratchet, onset×chute-tardio — ótimos por curva disjuntos
    # 10×); (5) a lei M⁻ do PRÓPRIO AUTOR, com o µ medido do próprio ensaio,
    # INVERTE a ordenação das vidas, erra razões até 4,65× e viola o limiar
    # D_cr do test1. Reabre se outra fonte exibir a assinatura N-explícita
    # (test3-like) que torne o canal de acumulação testável cross-rig.
    "chu2026ti_D0p4mm_F0_49kN_test2": (
        "form-limited com prova em lei (AGORA 6 degraus): onset/chute são "
        "função explícita de (D,F0) — estrutura que nenhuma forma nomeável "
        "carrega. O 6º degrau (2026-08-21): incubação ancorada + k_dmg_all "
        "melhoram 3,6-6,4× (→0,0430/0,0827/0,0374) e o σ TRAVA a 1,27× do "
        "limite real (0,0296) em TODAS as famílias varridas (relógio do "
        "dano, emb/creep lidos) — o trade-off dos 3 trechos do resíduo é "
        "circular. Adoção REVERTIDA pelo gate de censo (o prereg usara "
        "limite 0,0507 vencido; 4ª ocorrência do erro de limite). Rota "
        "parcial no prereg chu-test2-incubacao-damage"),
    "chu2026ti_D0p5mm_F0_49kN_test3": (
        "form-limited com prova em lei (5 degraus); fecha isolada com "
        "slip_onset_W=4000 (0,0402/0,0666/0,0264) — constante não transfere"),
    "chu2026ti_D0p7mm_F0_49kN_test4": (
        "form-limited com prova em lei (5 degraus); N90=406 > N90(0,4mm)=278 "
        "— não-monotonicidade em D que lei uniforme não tem"),
    "chu2026ti_D0p4mm_F0_61kN_test7": (
        "form-limited com prova em lei (5 degraus); vida 3,8× a do test2 com "
        "mesmo D — proteção de F0 mediada por µ(N), lei do autor inverte"),
    "chu2026ti_D0p4mm_F0_73kN_test8": (
        "form-limited com prova em lei (5 degraus); idem test7 (F0 73 kN)"),
    "chu2026ti_D0p5mm_F0_49kN_Ra1p6um_test9": (
        "form-limited com prova em lei (5 degraus); a mais próxima "
        "(0,0454/0,1056/0,0544) e sem alavanca que feche σ sem quebrar "
        "test5/6 — e a digitalização carrega discrepância Tabela-1 de 29% "
        "declarada na nota de aparato"),
    # §C forma faltante, máximo in-engine já aplicado
    # A liu2020_fig9_zinc_AF0.4mm SAIU em 2026-08-21 — fechou por mérito COM
    # a cauda de trinca incluída (emb do settling lido da própria curva);
    # prova em _EXCECOES_RETIRADAS_LIU2020_SETTLING.
    # A `jcsr2023_stainless_seawater` SAIU daqui em 2026-08-09 (D-AA): ela passa
    # o tripé por MÉRITO (0,0118/0,0304/0,0146). Prova preservada em
    # _EXCECOES_RETIRADAS_ADOCAO_JCSR — exceção retira da meta, mérito fecha a
    # curva, e trocar uma pela outra é ganho de leitura, não de contagem.
    "jcsr2023_plain_outdoor": "cliff/rebound de corrosão (forma faltante)",
    "yang2021_amp0p8mm_ax6kN": "canal estrutural ξ-dependente confundido",
    "yang2021_fig2_typical": "canal estrutural ξ-dependente confundido",
    # ASSINADA 2026-08-15 (delegação "eu assino tudo", pedido direto do
    # professor sobre esta curva às 15:09). Classe SUB-SLIP (a mesma das duas
    # yang2021 acima), com dossiê medido em yang2023_0p25_stick_resultado.md:
    # STICK permanente (slip=0 em 100% dos 4000 semiciclos instrumentados),
    # dado colapsa 42% enquanto só embedding/creep alcançam a curva (regra de
    # classe: alavanca de slip não chega); viés=+0,166=MAE (sinal único) com
    # ρ(res,N)=+0,96; o gth — única forma stick do engine, com o expoente 3,8
    # DO PRÓPRIO paper — foi varrido em 27 células: melhora no máx. −48%
    # (0,166→0,086) SEM fechar perna nenhuma (mx≥0,23 vs 0,10; σ≥0,095 vs
    # 0,025) e as células fortes destroem a canária 0,18-flat (+0,06..+0,57).
    # Inércia nas irmãs que deslizam: bit-idêntica (stick-only por
    # construção). Mesma estrutura do T13/YANG_2019: a forma trata a rampa,
    # não o colapso. Reabre com forma sub-slip nova ou dado de resolução
    # melhor (o paper segue paywalled; passos do dado 0,08).
    "10_Yang_2023_phenomenological_model__0_25_mm__2": (
        "sub-slip (stick 100% medido): dado colapsa sob stick e nenhuma "
        "alavanca alcança — gth (q=3,8 do próprio paper) varrido 27 células, "
        "máx. −48% sem fechar (0,086/0,296/0,113 na melhor)"),
    # §D família de sobreposição axial do Eccles (nova em 2026-07-27): a força
    # axial externa excede o torque de prevalência e o dado cru vai a ZERO. A
    # receita PR-31 piorou muito (G-B1 FAIL); o engine não tem condição de
    # contorno axial externa.
    "eccles2010_fig6_annotated_4kN_axial": (
        "sobreposição axial (G-B1 FAIL: receita PR-31 levou o res.máx de "
        "0.467 a 1.028) — o engine não tem contorno axial externo"),
    "eccles2010_fig8d_axial_3p5kN_intermittent": (
        "sobreposição axial (G-B1 FAIL: res.máx 0.252 -> 0.400 com a receita)"),
    "eccles2010_fig8b_axial_0p7kN_intermittent": (
        "sobreposição axial — e o FLOOR_TRIM corta 27 dos 35 pontos, logo o "
        "MAE 0.044 é pontuado sobre 8 pontos"),
    "eccles2010_fig7d_axial_3p1kN_constant": (
        "sobreposição axial — PASSA no tripé por ARTEFATO: o FLOOR_TRIM corta "
        "os 4 pontos da cauda a zero. Sai dos aprovados se a família for "
        "tratada como unidade"),
}


_F7_EXCECOES = {
    # Prova: o erro do modelo cabe DENTRO da repetibilidade medida da
    # fonte (`valor/piso`), logo nem um modelo perfeito passaria o limite
    # ali. FORTE = valor <= piso/raiz(2), a barra de "tão bom quanto o
    # centro das réplicas"; PROVA = valor <= piso. Derivação e as 33
    # RECUSADAS (modelo pior que a dispersão do dado) no documento.
    # As 9 que também estão na F5 ficam SÓ lá.
    #
    # RETIRADA DE 2026-07-30 (assinada em sessão): das 38 originais da F7,
    # **19 saíram para `_EXCECOES_RETIRADAS_D1`** — com o D1 adotado (limite da
    # 3ª perna = max(0,025; piso da fonte)) elas passam no tripé POR MÉRITO, e
    # a assinatura virou contabilidade dupla: a prova "o erro cabe no piso" É a
    # regra agora. Ficam aqui as que o D1 NÃO cobre, porque a perna que as
    # segura é MAE ou res.máx contra o piso (o D1 só move o σ_res), ou porque o
    # σ delas excede até o limite efetivo. Releitura completa:
    # `New_Theory/excecoes_releitura_posD1.md`.
    # "caccese2009_tapered_45kN_rep1" RETRATADA em 2026-08-04 —
    # ver _EXCECOES_RETRATADAS_CACCESE_PISO_INVALIDO (o piso 0.121 vinha do
    # pareamento mecânico cego que este mesmo arquivo passou a BLOQUEAR).
    # AS DUAS RETRATADAS em 2026-08-23 (prereg fecha-tickets-e-dedup),
    # _EXCECOES_RETRATADAS_ECCLES_PAR_DUPLICADO. O denominador estava INFLADO por
    # CONTAGEM DUPLA, e o defeito era MEU (commit 940a2c0): o par declarado entra
    # em `grupos` sob chave propria, e quando a chave automatica tambem o agrupa o
    # MESMO par conta 2x. A familia sem axial do ECCLES tem 4 membros (6 pares) e o
    # declarado e UM deles, pesado em dobro.
    # E nao era um par qualquer: medidos os 6 pares dado-contra-dado da familia, o
    # DECLARADO PELO AUTOR e o PIOR dos seis — mx 0.1866 e sigma 0.0707, os dois
    # MAXIMOS (os outros: fig3xfig7a 0.1104/0.0214 · fig3xfig8a 0.1109/0.0592 ·
    # fig3xfig8c 0.0756/0.0357 · fig7axfig8a 0.1846/0.0552 · fig7axfig8c
    # 0.0640/0.0203). Nenhum e outlier, logo a familia de 4 e LEGITIMA (medida, nao
    # assumida) e o piso correto e 0.0474/0.1220/0.0432, nao 0.0507/0.1543/0.0565.
    # Sob o piso deduplicado as duas FALHAM:
    #   fig8a  MAE 0.0489/0.0474 FALHA · mx 0.1320/0.1220 FALHA · sd 0.0395/0.0432 PROVA
    #   fig8c  MAE 0.0456/0.0474 PROVA · mx 0.1463/0.1220 FALHA · sd 0.0386/0.0432 PROVA
    # Custo declarado ANTES de medir: declarado_total 201 -> 199, fora_aberta 4 -> 6,
    # tripe INTACTO em 169. A alternativa era manter um piso que eu sabia inflado
    # para proteger duas excecoes que dependiam exatamente da inflacao. Precedentes
    # de retratacao por base invalida: ROUSSEAU, CACCESE, LU. O rigor vale contra nos.
    # PROVAS PRESERVADAS, verbatim:
    #   eccles2010_fig8a_no_axial_baseline1:
    #     prova de piso (PROVA): res.máx 0.1320/0.1543 · σ 0.0395/0.0565 — denominador RE-MEDIDO 2× e a
    #     2ª vez APERTOU. (1) 2026-08-15, prereg eccles-par-replica-declarado: o anterior (0.257/0.083)
    #     era o piso INVÁLIDO que a P-15 retratou — dispersão entre cargas axiais de 0 a 3,5 kN, a
    #     variável varrida do paper; o válido veio do par declarado fig8a×fig8c, baseline1/baseline2,
    #     rótulo DO AUTOR, ambos axial=0 (0.1866/0.0698). (2) 2026-08-23, prereg
    #     chave-estendida-pareamento: com a carga axial DENTRO da chave de família, as 4 curvas sem
    #     axial (fig3, fig7a, fig8a, fig8c) formam a família por MECANISMO em vez de por declaração, e
    #     o piso cai a 0.1543/0.0565. ⚠️ A margem de 4e-6 na barra FORTE do res.máx, que a versão de
    #     08-15 declarou não sobreviver a arredondamento, FOI CONSUMIDA: a barra virou 0.1091 e 0.1320
    #     > 0.1091, logo o res.máx é PROVA e não mais FORTE. O veredito da exceção NÃO muda — era PROVA
    #     (a perna mais fraca governa) e segue PROVA. Se alguém tivesse assinado FORTE ali, esta
    #     re-medição a derrubaria; a prudência de 08-15 é o que a salva. σ segue FORTE, por +0.0004.
    #   eccles2010_fig8c_no_axial_baseline2:
    #     prova de piso (PROVA): res.máx 0.1463/0.1543 · σ 0.0386/0.0565 — denominador RE-MEDIDO 2× e a
    #     2ª vez APERTOU. (1) 2026-08-15, prereg eccles-par-replica-declarado: o anterior (0.257/0.083)
    #     era o piso INVÁLIDO que a P-15 retratou — dispersão entre cargas axiais, a variável varrida
    #     do paper; o válido veio do par declarado fig8a×fig8c, rótulo DO AUTOR, ambos axial=0
    #     (0.1866/0.0698). (2) 2026-08-23, prereg chave-estendida-pareamento: com a carga axial DENTRO
    #     da chave, as 4 curvas sem axial formam família por MECANISMO e o piso cai a 0.1543/0.0565.
    #     Falha a barra FORTE no res.máx (0.1463 > 0.1091) e passa em PROVA — mesmo veredito de antes,
    #     com o denominador mais apertado, e a folga da perna que decide caiu de 0.0403 para 0.0080. σ
    #     segue FORTE, por +0.0013.
    # karlsen2022_M30_HV_run1p2: RETIRADA POR MÉRITO em 2026-08-06 (D-X) — o CSV
    # ancorava (1, 1.0000) num valor que a figura só atinge no ciclo ~26 (a curva
    # está soterrada no feixe inicial da Fig. 10), base 5,0 % baixa. Corrigidos
    # F₀ 315→331 kN e a CSV re-baseada: 0,0603/0,0940/0,0306 →
    # **0,0171/0,0434/0,0195** ⇒ passa o tripé pelos limites GLOBAIS, sem
    # precisar de exceção. Prova antiga preservada: "FORTE: MAE 0.060/0.235 ·
    # σ 0.031/0.174" (contra o piso que o próprio D-X invalidou).
    # karlsen2022_M30_HVtorqued_run14p2: RETRATADA — ver
    # _EXCECOES_RETRATADAS_F7_PERNA_DESCOBERTA.
    # rousseau2025_{hdpe_t10,hdpe_t12,steel_t10}: RETRATADAS em 2026-08-01 —
    # ver _EXCECOES_RETRATADAS_ROUSSEAU_PISO_INVALIDO (o piso 0.546/0.206/
    # 0.186 vinha do par aco-t10<->aco-t12, ESPESSURAS diferentes pareadas
    # como replicas porque a chave mecanica e' cega a geometria per-case; e
    # o proprio drive do aco estava 10x errado no registry).
    # LU_2024 — leva de 2026-07-31 (noite), assinada por delegação, contra os
    # As 5 provas por piso de condição do LU_2024 (fig18_amp0p5, fig20_T10/
    # T16/T22/T28) foram RETRATADAS em 2026-08-14 — ver
    # _EXCECOES_RETRATADAS_LU_PROTOCOLO: os pares fig14×fig18/20 que davam os
    # pisos cruzavam PROTOCOLOS (§3.1.3 half-sine máquina × §3.2 manual, dito
    # pelo próprio paper). 4ª retratação por pareamento inválido da campanha.
}
# RETRATADAS em 2026-08-14 — QUARTA retratação por pareamento inválido, a
# maior (5 assinaturas de uma vez), e desta vez a prova é o TEXTO do paper:
# as corridas longas ("fig14_*_long") são a §3.1.3 — half-sine, controle de
# MÁQUINA, 1 Hz, F0 iniciais 12.398/12.285/12.696 N (p.14) — e as Fig.18/20
# são a §3.2, que abre dizendo que o controle MANUAL "elimina os efeitos da
# half-sine" (p.15). Protocolos diferentes não são réplicas. Medido antes da
# leitura (commit 9784148): tempo até 0,90·F0 difere 27–56×, plateau SEMPRE
# do lado §3.1.3, 3/3 — e a direção é a do achado de frequência do próprio
# paper (§3.1.2: frequência menor ⇒ mais afrouxamento por ciclo; manual ≈
# ultrabaixa). Os pisos por condição (1,0mm 0,519/0,850/0,304 etc.) mediam
# DIFERENÇA DE PROTOCOLO, não repetibilidade. Exposição por curva no momento
# da retratação (store 55273eab12b0, dado corrigido): T22 0,052/0,255/0,060
# (MAE a 4% do limite — a menos exposta); amp0p5 0,126/0,180/0,078; T16
# 0,173/0,442/0,086; T28 0,110/0,270/0,093; T10 0,288/0,802/0,155 (a mais
# dependente do piso grande). Efeito no censo: −5 resolvidas; o rigor vale
# contra nós (precedentes ROUSSEAU/CACCESE/LU-07-31). A fonte fica SEM piso
# de réplica válido (o par T22↔fig18_amp1p0 é DIGITALIZAÇÃO, mesmo teste em
# 2 figuras, < global) ⇒ `limite_sres(LU)` volta ao global 0,025.
_EXCECOES_RETRATADAS_LU_PROTOCOLO = {
    "lu2024_M8_fig20_T10Nm": (
        "RETRATADA: prova citava piso de par §3.1.3×§3.2 (protocolos "
        "distintos pelo próprio paper); era PROVA MAE 0.288/0.519"),
    "lu2024_M8_fig20_T16Nm": (
        "RETRATADA: mesmo par inválido; era FORTE MAE 0.173/0.519"),
    "lu2024_M8_fig20_T22Nm": (
        "RETRATADA (2ª vez — a re-assinatura de 2026-07-31 trocou um par "
        "inválido por outro): era FORTE MAE 0.052/0.519; a curva está a 4% "
        "do limite de MAE por mérito"),
    "lu2024_M8_fig20_T28Nm": (
        "RETRATADA: mesmo par inválido; era FORTE MAE 0.110/0.519"),
    "lu2024_M8_fig18_amp0p5": (
        "RETRATADA: mesmo par inválido; era FORTE MAE 0.126/0.263"),
}
# RETRATADAS em 2026-07-31 (mesma noite da assinatura, pego pelo RIGOR do
# gate elastico — a prova F7 exige TODAS as pernas violadas cobertas pela
# barra, e a leva citou so o MAE): fig14_amp0p5 tem mx 0.604 > PROVA-mx
# 0.569 (6%); fig14_amp1p0 tem σ 0.333 > PROVA-σ 0.159 (2.1×). Ficam FORA
# com procedencia (fila honesta; scatter cobre o MAE mas nao a forma).
# RETRATADA em 2026-08-07 — **P-11 ASSINADA pelo professor**. A classe F5 de
# *scatter* provava **unalcançabilidade da FAMÍLIA** ("nenhum modelo
# determinístico único pode ficar dentro da meta") e, por isso, **não tinha
# limite superior algum**: formalmente cobriria uma curva com res.máx 1,0. A
# P-11 acrescentou o mesmo teste POR CURVA que o F7 já aplica — o erro não
# pode exceder o desvio-à-mediana da família.
# Medido: 8 das 9 estão ABAIXO da estatística da família (0,34× a 0,52×) e
# sobrevivem com folga de 2–3×. Só esta está acima — o que é evidência de que
# a guarda é DISCRIMINANTE, não decorativa. Não houve deriva: o próprio
# `f5_excecoes_propostas.md` registra res.máx 0,3965, o valor de hoje.
_EXCECOES_RETRATADAS_P11 = {
    "bauer2024_M12_fig8_test1":
        "scatter de réplicas SEM limite superior: res.máx 0,3965 > "
        "desvio-à-mediana 0,349 da família fig8 (1,14×). MAE 0,0745 e "
        "σ 0,0928 também ficam fora do que a prova enderesa. "
        "DESTINO: virou DECLARAÇÃO por colapso na P-12 (mesma data) — a "
        "exceção era improcedente, mas a curva tem cobertura assinada",
}
# Retirada porque a curva passou a FECHAR POR MÉRITO (K6) — adoção
# 2026-08-20 do limiar do espectro por espécime (prereg
# bauer-fig8-scrit-especime): o grupo fig8 já rodava graded + espectro mas
# com s_crit_loose=0, e sem o limiar a transição de fração do espectro
# (2/20 → 20/20 ciclos ativos) — a física da PRÓPRIA nota de aparato — não
# existia no modelo.
_EXCECOES_RETIRADAS_BAUER_SCRIT = {
    "bauer2024_M12_fig8_test2": (
        "era 'scatter de réplicas (desvio-à-mediana 0.349)'; fechou com "
        "s_crit=30µm·k=0,06 por espécime: 0,0290/0,1795/0,0461 → "
        "0,0149/0,0419/0,0187 (região 4/4 vizinhos). O test3 da mesma prova "
        "FICA — a célula dele é navalha medida (0/4 vizinhos)"),
}
# (2026-08-21: uma retirada do chu test2 foi ESCRITA aqui e DESFEITA no mesmo
# dia — o pacote incubação+k_dmg_all melhorava 3,6-6,4× mas o σ 0,0374 não
# fecha o limite REAL da fonte, 0,0296; o prereg usou 0,0507 vencido. A
# exceção segue ativa com a nota do ataque. Fica o registro para que a
# sequência edição→reversão seja auditável no git.)
_EXCECOES_RETIRADAS_LIU2020_SETTLING = {
    "liu2020_fig9_zinc_AF0.4mm_P0-18kN": (
        "era 'trinca de fadiga §3.1.2 (changepoint não achou o corte)'; "
        "fechou em 2026-08-21 (prereg liu2020-af04-emb-settling) COM a cauda "
        "incluída: |viés|/MAE=1,00 era puro nível — o emb da fonte (1,12µm, "
        "de outra condição) não cobria o settling de ~7% da MAIOR amplitude "
        "da série; emb 3µm/N_emb 60 LIDOS da própria curva (região 9/9, "
        "token específico af0.4 ANTES de zinc — first-match casa 7 curvas) ⇒ "
        "0,0526/0,0766/0,0227 → 0,0082/0,0232/0,0100"),
}

_EXCECOES_RETRATADAS_F7_PERNA_DESCOBERTA = {
    "lu2024_M8_fig14_amp0p5_long": "mx 0.604/0.569 nao coberto",
    "lu2024_M8_fig14_amp1p0_long": "σ 0.333/0.159 nao coberto",
    # 2026-08-06 (D-X) — e esta retratação foi CRIADA pela nossa própria
    # correção, o que a torna obrigatória de registrar: sob o piso INVÁLIDO
    # (σ 0,1742, inflado pelo par Vibralock×HV) a perna σ da run14p2 nem
    # violava (0,49×). Bloqueada a chave cega, o piso válido é σ **0,0845**
    # e aí σ = 0,0854 **viola** (1,01×) **e fica DESCOBERTA** — por **1,1 %**,
    # a margem mais fina de toda a campanha (as anteriores foram 6 % e 2,1×).
    # Registrado com o número à vista porque a decisão é apertada: o piso vem
    # de **n=2**, e declarar a família M30-HV (4 espécimes) cobriria a perna —
    # mas ao preço de um piso σ de 0,1644 (6,6× o global), que foi RECUSADO.
    # Custo: resolvida −1.
    # ⚠️ ATUALIZADO em 2026-08-07 (pós-**D-Y**, store `1c118e405a42`): a
    # retratação SEGUE VÁLIDA, mas **pela razão OPOSTA** — o texto anterior
    # ("MAE 0,0898/0,1031 e res.máx 0,2363/0,2468 seguem cobertas, só o σ
    # caiu") ficou FALSO e está corrigido aqui. Corrigida a base da `run2p2` e
    # declarado o par, os três pisos da fonte mudaram juntos:
    #     MAE  0,1031 → **0,0840**   res.máx 0,2468 → **0,2230**
    #     σ    0,0845 → **0,0903**
    # ⇒ a perna σ **deixou de violar** (0,0854 ≤ 0,0903) e as pernas MAE e
    # res.máx, que estavam cobertas, ficaram **DESCOBERTAS** (0,0898 > 0,0840;
    # 0,2363 > 0,2230). Passou de UMA perna descoberta para DUAS: o D-Y não
    # devolveu a exceção, piorou-a.
    # Leitura física do que a correção fez: removido o erro de BASE (que é
    # deslocamento de NÍVEL), as duas réplicas passam a concordar melhor em
    # nível — pisos de MAE e res.máx CAEM — e a dispersão restante é de FORMA,
    # que o piso de σ então mede maior. É o §4.43 acontecendo: registro medido
    # contra `5916d8be0510` vira suspeito assim que o fingerprint muda.
    "karlsen2022_M30_HVtorqued_run14p2":
        "MAE 0.0898/0.0840 e res.max 0.2363/0.2230 nao cobertos sob o piso "
        "pos-D-Y (o sigma deixou de violar: 0.0854 <= 0.0903)",
}
# RETRATADA em 2026-07-31 (mesma data da assinatura, ao LER O PAPER): a
# exceção da lu2024_M8_fig20_T22Nm foi assinada sobre um PISO INVÁLIDO — o
# "par" fig18_amp0p5↔fig20_T22Nm cruzava 0,5 mm contra 1,0 mm (a fig20 roda
# a 1,0 mm: p.19 do PDF + Tabela 9 ≡ Tabela 8 na linha 22 N·m). O σ 0,0909
# media diferença de AMPLITUDE, não repetibilidade. O par verdadeiro
# (amp1p0↔T22, mesmo teste em 2 figuras) mede σ 0,0210/MAE 0,0131 — piso de
# DIGITALIZAÇÃO, fraco demais para F7. Fica como registro; a prova de piso
# válida desta fonte depende da Fig. 14 (3 réplicas reais documentadas).
# Ver `lu2024_plano_melhoria.md` A2.
_EXCECOES_RETRATADAS_LU_PISO_INVALIDO = {
    "lu2024_M8_fig20_T22Nm": (
        "RETRATADA: prova usava piso de par cruzado 0,5×1,0 mm"),
}
# RETRATADA em 2026-08-04 — TERCEIRA retratação por piso inválido, e a causa é
# rastreável a uma correção feita neste mesmo arquivo: a assinatura usava piso
# MAE **0,121**, vindo do pareamento mecânico CEGO (chave δ=0 ∧ F_amp=0) que
# juntava as 7 condições distintas do CACCESE_2009 — compblock 34/71 kPa,
# protruding, tapered, retighten 12,7/19,1 mm — como se fossem réplicas. Esse
# pareamento foi BLOQUEADO ao pôr `CACCESE_2009` em `_SEM_FAMILIA_MECANICA`, e
# o par VÁLIDO (rep1↔rep2, mesma condição, declarado em
# `_PARES_REPLICA_DECLARADOS`) mede pelo helper do report:
# MAE **0,03719** · res.máx 0,06762 · σ 0,02337 (n=2, janela comum 0..2000).
# Barra PROVA do MAE = 0,0372; o modelo faz **0,0523** ⇒ perna DESCOBERTA, a
# 3,2× do piso que a assinatura citava. A regra vigente (precedente LU_2024) é
# explícita: *a barra usa o piso da MESMA condição, nunca a média da fonte*.
# Efeito no censo: −1 resolvida. Registrado porque a rigor de 2026-07-31
# ("F7 exige TODAS as pernas violadas cobertas") vale contra nós também.
#
# ⚠️ **O 0,0523 acima está VENCIDO, e a data explica por quê** (§4.43 aplicada
# contra nós): foi medido em 2026-08-04, ANTES da adoção **D-H** (kernel de
# creep saturante nesta mesma fonte, adotada no mesmo dia). No store vigente
# `b072b24fd3a8` a `rep1` faz **MAE 0,0203 · res.máx 0,0260 · σ 0,0054** e
# **PASSA O TRIPÉ POR MÉRITO** ⇒ a retratação continua CORRETA (o piso citado
# era inválido) mas ficou **sem consequência**: a curva não precisa de exceção
# nenhuma. Se a rota F7 fosse reaberta hoje, o MAE 0,0203 estaria **abaixo** da
# barra PROVA 0,0372 — perna coberta, não descoberta. Fica como registro de
# método: número de RETRATAÇÃO também envelhece, e quem o lê sem o fingerprint
# conclui o oposto do que o store diz.
_EXCECOES_RETRATADAS_CACCESE_PISO_INVALIDO = {
    "caccese2009_tapered_45kN_rep1": (
        "RETRATADA: prova usava piso 0,121 de pareamento cego entre as 7 "
        "condições da fonte; piso válido do par rep1↔rep2 é MAE 0,0372 "
        "e o modelo faz 0,0523 (DESCOBERTA)"),
}
# Medido na mesma passada e registrado para não ser re-tentado: a `rep2` **não
# tem rota F7**. A única perna que ela viola é o σ (0,0354 contra o limite
# 0,0250) e o piso de σ do par é **0,0233** — abaixo do limite global e abaixo
# do erro do modelo. As duas réplicas do DADO concordam 1,5× melhor que o
# modelo concorda com elas: não há o que provar.
# RETIRADA em 2026-08-05, no MESMO dia em que foi proposta (D-M) — e retirada
# porque deixou de ser NECESSÁRIA, não porque estivesse errada.
#
# A `liu2022_fig8_multi_t4` termina em FRATURA POR FADIGA a ~1500 ciclos
# (documentado em 3 lugares independentes desde 2026-07-03, verificado por
# `git log -S`: commits 3931f1c e 8acad71) e o cfg do grupo NÃO tem canal de
# fadiga (zero chaves `fat*`) ⇒ o mergulho terminal é inproduzível por
# construção. O argumento de escopo É válido e os gates G1–G4 do prereg o
# confirmaram.
#
# O que mudou: o D-M foi escrito porque esta curva BLOQUEAVA o G4 do D-L. Ao
# aplicar a disciplina de fronteira de grade (`bounds_saturated`, pré-teste 3
# do charter) e estender a varredura, apareceu uma célula com **ZERO violações
# do G4** — a adoção não precisa da declaração. Como o mandato proíbe declarar
# curva como consequência de um gate, e a declaração deixou de ter função,
# retirá-la é o que remove a ambiguidade em vez de conviver com ela.
#
# Custo, declarado: resolvida/declarada volta de 172 para **171/205**;
# declaradas 16 -> 15; a curva volta à fila form-limited, onde estava desde
# 2026-07-03. A leitura estrita não se move (ela nunca esteve no tripé).
#
# O argumento de escopo fica AQUI, preservado e disponível: é decisão do
# professor promovê-lo a declaração, e a procedência não expira.
_DECLARACAO_DISPONIVEL_NAO_TOMADA = {
    "liu2022_fig8_multi_t4":
        "escopo de mecanismo: fratura por fadiga a ~1500 ciclos (3 registros "
        "independentes desde 2026-07-03); grupo sem canal de fadiga ⇒ mergulho "
        "inproduzível por construção. Rota por mérito recusada com número "
        "(rampa D_on=0,75/q=8 é navalha: leva F₀ a 0 onde o dado pede mergulho "
        "parcial para 0,845). NÃO declarada: a adoção do relógio por reaperto "
        "não precisou dela, e declarar como consequência de gate é proibido",
}

# ⚠️ **RE-MEDIDO em 2026-08-05 e o diagnóstico MUDOU DE LADO.** O σ 0,0354 era
# pré-D-H; no store `b072b24fd3a8` a `rep2` faz **σ 0,02576** — viola por **3 %**,
# não por 42 %. E a investigação do piso (`caccese_piso_e_dado_resultado.md`,
# extração VETORIAL da Fig. 9, resíduo de calibração 2,3e-5) achou a causa:
# **9 dos 26 pontos da nossa CSV `rep2` traçam a curva ERRADA** (a média, não a
# baixa), com erro +0,040 a +0,054 em t=50..1000 h. Duas provas internas que
# dispensam o paper: (i) `rep2` é **idêntico ao dígito** à `rep1` em t=900
# (0,7087) e t=1000 (0,7081) — duas réplicas independentes não concordam a 4
# decimais; (ii) `rep2` é **não-monótona** num ensaio de relaxação estática em
# que TODOS os traços publicados decrescem. Com o dado corrigido o σ cai
# **3,1×** (0,0258 → 0,0083) e a curva **PASSA POR MÉRITO**, sem tocar no modelo
# e sem exceção. O piso verdadeiro do rig é σ **0,002–0,009** (4 instrumentos
# independentes, incl. os ajustes Eq. (2) do próprio paper) ⇒ sempre < 0,025 ⇒
# `limite_sres` fica no global em TODOS os cenários, inclusive com a **3ª
# réplica** (a Fig. 9 tem TRÊS tapered; digitalizamos duas). A rota "piso maior
# ⇒ exceção" segue **fechada por medição**; o que estava errado era o DADO.
_SEM_ROTA_F7_MEDIDO = {
    "caccese2009_tapered_45kN_rep2": (
        "σ 0,02576 > limite 0,0250 (3 %, única perna) e o piso do par é 0,0083 "
        "⇒ sem rota F7. Defeito RE-ATRIBUÍDO ao DADO em 2026-08-05: 9 de 26 "
        "pontos da CSV traçam a réplica errada; corrigido, σ 0,0083 e passa"),
}
# RETIRADAS em 2026-07-30 (D1): passam no tripé pela regra `limite_sres`, a
# assinatura deixou de ser necessária. NÃO consumidas por `_EXCECOES` — ficam
# como REGISTRO em código (a prova assinada de cada uma, preservada) e para o
# teste de reversão: se o D1 for revertido, é ESTA lista que volta para a F7 no
# mesmo commit. Cross-check da lista: `excecoes_releitura_posD1.md` §A, gerado
# por recomputação (documento e recomputo idênticos, conferido na retirada).
_EXCECOES_RETIRADAS_D1 = {
    "bauer2024_M8_fig6_rep2": (
        "prova de piso (FORTE): σ 0.034/0.090"),
    "bauer2024_M8_fig6_rep3": (
        "prova de piso (FORTE): σ 0.038/0.090"),
    "chu2026ti_D1p0mm_F0_49kN_test5": (
        "prova de piso (PROVA): σ 0.044/0.051"),
    "chu2026ti_D1p0mm_F0_49kN_test6_repeat": (
        "prova de piso (FORTE): σ 0.029/0.051"),
    "demir2024_amp0p3_F14p3_lk13p8": (
        "prova de piso (PROVA): σ 0.043/0.057"),
    "demir2024_amp0p3_F14p3_lk19p8": (
        "prova de piso (FORTE): σ 0.034/0.057"),
    "demir2024_amp0p3_F17p6_lk13p8": (
        "prova de piso (PROVA): σ 0.044/0.057"),
    "demir2024_amp0p3_F17p6_lk19p8": (
        "prova de piso (FORTE): σ 0.029/0.057"),
    "demir2024_amp0p4_F17p6_lk13p8": (
        "prova de piso (FORTE): σ 0.036/0.057"),
    "eccles2010_fig7c_axial_2p7kN_constant": (
        "prova de piso (FORTE): σ 0.026/0.083"),
    "jcsr2023_galv_seawater": (
        "prova de piso (FORTE): σ 0.047/0.221"),
    "jcsr2023_plain_seawater": (
        "prova de piso (FORTE): σ 0.037/0.221"),
    "karlsen2022_M30_HV_run2p2": (
        "prova de piso (FORTE): σ 0.055/0.174"),
    "karlsen2022_M30_HV_run6p2": (
        "prova de piso (FORTE): σ 0.030/0.174"),
    "karlsen2022_M30_HV_run7p1": (
        "prova de piso (FORTE): σ 0.050/0.174"),
    "karlsen2022_M42_HV_run21p0": (
        "prova de piso (FORTE): σ 0.034/0.174"),
    "rousseau2025_hdpe_t14": (
        "prova de piso (FORTE): σ 0.030/0.186"),
    "rousseau2025_steel_t12": (
        "prova de piso (FORTE): σ 0.031/0.186"),
    "sun2025efa109235_transverse_grease_crimp": (
        "prova de piso (FORTE): σ 0.030/0.066"),
}
# RETIRADA de 2026-07-30 (noite, por delegação — mandato da sessão): com a
# adoção LIU_2016 (fretting L1) a curva passa no tripé POR MÉRITO
# (MAE 0.0504→0.0442) e a assinatura virou contabilidade dupla — o MESMO
# critério da retirada D1. Detectada pelo invariante
# `test_excecao_assinada_esta_de_fato_fora_do_tripe`, não a olho. Se a
# adoção LIU_2016 for revertida, esta entrada volta para a F7 no mesmo
# commit.
_EXCECOES_RETIRADAS_ADOCAO_LIU2016 = {
    "liu2016wear_fig9a_m45nm": (
        "prova de piso (FORTE): MAE 0.050/0.102"),
}
# D-AA (2026-08-09) — a curva passou por MÉRITO e a assinatura virou redundante.
# A prova ORIGINAL fica aqui: ela dizia "cliff/rebound de corrosão (forma
# faltante)", diagnóstico do F3.1-JCSR de 2026-07-21 que classificava a curva
# como piso ESTRUTURAL. O diagnóstico não era mentira — era conclusão sobre uma
# varredura MARGINAL (α×t_c com C fixo, e C com a forma fixa), e forma e nível
# do creep são acoplados por construção (δ_sat = C_creep·F_0·(1−e^{−(t/t_c)^α}):
# assíntota em C_creep, chegada em α/t_c). A varredura CONJUNTA estendida achou
# região INTERIOR de 10 células e a curva fechou em 0,0118/0,0304/0,0146 — de
# res.máx 1,24× a 0,30×. Registro: `New_Theory/jcsr_acoplamento_forma_nivel_
# resultado.md`, prereg `2026-08-09-jcsr-acoplamento-forma-nivel-prereg.md`.
_EXCECOES_RETIRADAS_ADOCAO_JCSR = {
    "jcsr2023_stainless_seawater": (
        "cliff/rebound de corrosão (forma faltante) — era 0,0619/0,1237/0,0739"),
}
# RETIRADA em 2026-08-16 (prereg `2026-08-16-lu2024-pico-espurio`, adendo A3).
# A curva era DECLARADA "órfã de protocolo" (item F) e passou a fechar o tripé
# POR MÉRITO quando o artefato de digitalização saiu do CSV: 0,0364 / 0,0735 /
# 0,0212 contra 0,05 / 0,10 / 0,025.
#
# ⚠️ O que isto ensina, e é mais importante que a curva: a declaração dela
# repousava, em parte, num DEFEITO DE DADO. O ponto espúrio em x=80 fazia a
# curva cair 0,352 → 0,072 entre pontos vizinhos — salto de 0,28, acima do
# limiar de 0,25 do classificador — e ela era contada como *metric-limited por
# colapso quase-vertical*. O "colapso" era o artefato. A camada
# `metric_limited_colapso` foi de 1 para **0** com a correção.
#
# A retirada é obrigatória, não cosmética: enquanto a curva ficasse na lista, o
# `declarado_total` a contaria DUAS vezes (o mesmo defeito que o K6 da adoção
# JCSR expôs em 2026-08-09). Quem denunciou foi a guarda-espelho
# `test_medicoes_cruzadas::test_excecao_assinada_esta_de_fato_fora_do_tripe`.
_DECLARACOES_RETIRADAS_PICO_ESPURIO = {
    "lu2024_M8_fig20_T22Nm": (
        "era 'órfã de protocolo' (item F, 2026-08-14) e também metric-limited "
        "por colapso — o colapso era o pico espúrio em x=80 (0,085 → 0,352 → "
        "0,072). Sem ele: 0,0364/0,0735/0,0212, fecha por mérito"),
}
# Retiradas porque a curva passou a FECHAR POR MÉRITO após adoção gateada —
# mesmo estatuto K6 (declaração que fica depois do mérito conta 2× no
# `declarado_total`). A prova de que a declaração era legítima QUANDO feita
# fica aqui; o item F continua válido para as irmãs.
_DECLARACOES_RETIRADAS_FECHAM_POR_ADOCAO = {
    "lu2024_M8_fig20_T28Nm": (
        "era 'órfã de protocolo' (item F, 2026-08-14; 0,1008/0,1969/0,0862 — "
        "sem rota de piso nem de dado). Fechou por MODELO em 2026-08-20 "
        "(prereg lu2024-t28-piso-lido): floor LIDO 0,2414 do terminal "
        "PUBLICADO (Tabela 9: 0,234; p.19 3523 N, coincidem a 3,2%) + "
        "arrest_approach_exp 1,4 fitado-declarado (região de 9 células) ⇒ "
        "0,0338/0,0649/0,0181. 1ª órfã de protocolo a fechar por mérito — a "
        "rota de modelo do item F era 'falsificada' para a forma half-sine, "
        "não para o piso lido, que não existia à época (precedente SUN/T10 "
        "é de 2026-08-19)"),
    "lu2024_M8_fig18_amp1p5": (
        "era 'órfã de protocolo' (item F; 0,0314/0,0742/0,0353 — só o σ "
        "violava, 1,41×). Fechou por MODELO em 2026-08-20 (prereg "
        "lu2024-amp1p5-aexp-regredido): arrest_approach_exp 1,864 REGREDIDO "
        "do dado cru (r²=0,685, dentro da região que fecha 1,5–3,0; floor do "
        "grupo intocado — o floor lido 0,0176 foi FALSIFICADO: piora) ⇒ "
        "0,0139/0,0393/0,0157"),
    "10_Yang_2023_phenomenological_model__0_45_mm__4": (
        "era metric-limited por colapso (Δdado>0,25; 0,1042/0,3600/0,1344). "
        "A releitura do CRU mostrou que o salto é passo de AMOSTRAGEM "
        "(x pula 20→50), não parede — o closed-form P-13 cruza os pontos a "
        "0,011. Fechou em 2026-08-20 (prereg ijpem-045-055-p13) com o pacote "
        "das irmãs 0_30/0_35/0_50 ⇒ 0,0102/0,0154/0,0115; n=6 na janela ⇒ "
        "σ julgável, diferente da 0_55"),
    "bauer2024_M12_fig8_test1": (
        "era metric-limited por colapso (Δdado 0,264>0,25; "
        "0,0745/0,3965/0,0928). O 'colapso' é a TRANSIÇÃO DE FRAÇÃO DO "
        "ESPECTRO (2/20 → 20/20 ciclos ativos quando o slip da base 80µm "
        "cruza o limiar — a física da própria nota de aparato) e o grupo "
        "rodava s_crit_loose=0. Fechou em 2026-08-20 (prereg "
        "bauer-fig8-scrit-especime): s_crit=15µm·k=0,070 por espécime ⇒ "
        "0,0305/0,0719/0,0282 (limite σ da fonte 0,0900; região 7/9 células). "
        "2ª metric-limited a cair por releitura do 'colapso' (1ª: 0_45)"),
    "lu2024_M8_fig20_T16Nm": (
        "era 'órfã de protocolo' (item F; 0,1572/0,2384/0,0578). O mapa de "
        "rotas errava o diagnóstico ('meio-de-rampa'): o mx era o 1º CICLO "
        "(excesso de embedding −0,164) e dali o modelo converge ao floor "
        "lido (−0,005 em c99). Fechou em 2026-08-20 (prereg "
        "lu2024-t16-emb-ancorado): floor 0,195 LIDO (terminal publicado "
        "0,187, 4,3%) + emb_depth 4µm ANCORADO no 1º ciclo (modelo 0,594 vs "
        "0,588 digitalizado; c1 publicado Tabela 9) ⇒ 0,0226/0,0569/0,0249 "
        "— margem σ de 0,4% declarada (precedente D-V)"),
    "yang2023ame_axial": (
        "era 'fora de escopo de material' (CFRP; 0,3875/0,4654/0,1139 — "
        "aprovada pelo professor em 2026-07-31). O diagnóstico estava "
        "INVERTIDO: o dado quase não perde (10% em 1100 ciclos, suave) — o "
        "MODELO despencava 45% por emb default 11µm instantâneo (fonte sem "
        "grupo adotado). A 'relaxação viscoelástica que faltava' é o "
        "embedment PROGRESSIVO que os próprios autores nomeiam (nota G8) e "
        "o EmbeddingLoss state-based já faz com relógio lento. Fechou em "
        "2026-08-20 (prereg yang2023ame-emb-lento): emb 32µm·N_emb 17000 "
        "(degenerescência alvo↔relógio declarada; taxa 8e-5/c regredida do "
        "cru r²=0,92) ⇒ 0,0285/0,0388/0,0103. O escopo cai PARA ESTA "
        "JANELA/CARGA; extrapolação de longo prazo segue não-validada"),
    "lu2024_M8_fig14_amp1p0_long": (
        "era 'órfã de protocolo' (item F) e a PIOR declarada do projeto "
        "(0,4802/0,8553/0,2894 — 9,6× o MAE). Fechou em 2026-08-21 (prereg "
        "lu2024-fig14-burst) com a forma NOVA onset_burst_* (liberação da "
        "energia incubada) + o achado de que o bedding fracional do grupo "
        "era do protocolo MANUAL (emb_load_frac=0 lido do protocolo): "
        "frac=0,62 LIDO da inflexão do burst, fe=1,24 lido da cauda, W=360 "
        "ancorado no platô de 54 ciclos ⇒ 0,0136/0,0882/0,0186 (região de "
        "6 células). A irmã amp0p5_long melhora 2,6× e NÃO fecha (2 regimes "
        "pós-burst) — segue declarada com custo declarado"),
    "lu2024_M8_fig14_amp0p25_long": (
        "era 'órfã de protocolo' (item F; 0,1017/0,2314/0,0367). Fechou em "
        "2026-08-21 (prereg lu2024-amp0p25-emb-lido) com pacote de LEITURA "
        "QUASE PURA — ZERO fitados: emb 6µm ancorado no platô publicado "
        "(0,171·F₀/k_b), N_emb=30 lido do degrau (x=16-32), frac=0 do "
        "protocolo, creep/ratchet=0 lidos do arresto perfeito (1000 ciclos "
        "sem deriva) ⇒ 0,0077/0,0630/0,0156 (região 12/12). ERRATA do mapa "
        "(4ª): não era sigmoide — degrau+arresto é exponencial de relógio "
        "curto; a forma Weibull construída no caminho fica DORMENTE"),
}
# A união é o que vale para badge, filtro e contagem.
_EXCECOES = {**_F5_EXCECOES, **_F7_EXCECOES}

# DECLARADAS (Camada 2 da regra de parada, assinada por delegação 2026-07-30 —
# mandato "fique à vontade para tomar quaisquer decisões"). NÃO são exceções de
# mérito nem contam como "o modelo acerta": são curvas em que a MÉTRICA ou o
# DADO não decidem, e declará-las separa "o modelo errou" de "não dá para
# julgar" — hoje somados. Critérios MEDIDOS (triagem_posD1.json, reproduz com
# `py -3.12 New_Theory/regra_de_parada_triagem.py`):
#   · não-julgável: n < 6 pontos na janela da métrica ⇒ σ_res sem suporte
#     estatístico (decisão (b) do handoff: SIM, vira classe declarada);
#   · metric-limited: |Δdado| > 0,25 entre pontos consecutivos — colapso
#     quase-vertical que nenhuma métrica automática resolve (§4.44–§4.48a, a
#     linha de metrica fechada do estudo LIU_2025);
#   · data-limited por PROVENIÊNCIA (2026-07-31, por delegação): a figura de
#     origem é ROTULADA pelo próprio paper como ilustração — cobrar o modelo
#     contra um desenho redesenhado não é validação (critério = o rótulo
#     impresso + a nota de aparato que documenta as feições desenhadas).
# A leitura publicada é SEMPRE dupla (decisão (c): as duas, juntas): ESTRITA =
# tripé; RESOLVIDA/DECLARADA = tripé + exceções + declaradas.
# (2026-08-01: amp2p0 SAIU por MÉRITO — passa o tripé sob o ponto R4
# adotado, 0,046/0,072/0,023; precedente da m45nm.)
# (2026-07-31 noite: amp0p5/T10/T16/T28 SAÍRAM daqui — ganharam exceção F7
# por prova de piso de condição, e exceção supersede declaração; a natureza
# de colapso segue documentada na proveniência da exceção.)
# RETRATADAS em 2026-08-07 — **P-10 ASSINADA pelo professor**. O critério
# "data-limited por resolução" (2026-08-01) media **só o passo do DADO** e
# nunca o comparava ao ERRO do modelo. Seu próprio argumento — *"entre dois
# pontos medidos o dado não restringe a curva a menos do que o passo"* — exige
# erro DA ORDEM do passo; quando o erro é 2× ou 4× o passo, ele **é**
# mensurável e a justificativa cai. A guarda acrescentada pela P-10:
#     mediana |Δdado| ≥ META_MAX **E** res.máx ≤ mediana |Δdado|.
# ⚠️ O achado nasceu de uma tentativa MINHA de fechar a fila form-limited em
# zero declarando a `karlsen_run14p2` por este critério: ela qualificava pela
# LETRA (mediana 0,1216 ≥ 0,10) e o controle da própria fonte refutou — quatro
# irmãs com amostragem MAIS GROSSA passam com erro em 0,33–0,57 do passo,
# enquanto ela erra 1,94×. O mesmo teste voltou contra estas três, que já
# contavam a nosso favor. Custo: resolvido-ou-declarado −3.
_DECLARACOES_RETRATADAS_P10 = {
    "10_Yang_2023_phenomenological_model__0_30_mm__8":
        "citava resolução: passo 0,1800 mas res.máx 0,2200 (mx/passo 1,22) "
        "— sem critério alternativo",
    "10_Yang_2023_phenomenological_model__0_35_mm__3":
        "citava resolução: passo 0,1400 mas res.máx 0,5600 (mx/passo 4,00) "
        "— o pior caso; sem critério alternativo",
    "10_Yang_2023_phenomenological_model__0_50_mm__9":
        "citava n<6, que exige as pernas JULGÁVEIS passando (MAE de 5 pontos "
        "é julgável) e o MAE dela erra 4,77×; resolução também falha "
        "(mx/passo 1,82) e o colapso não se aplica (max|Δdado| ≤ 0,25)",
}
# RE-MOTIVADAS na mesma assinatura (seguem DECLARADAS, motivo corrigido):
# 0_55 -> colapso (res.máx a 0 índices do penhasco) · 0_65 -> resolução COM a
# guarda nova (mx/passo 0,76). Uma declaração vale se QUALQUER critério
# assinado a cobre — retratá-las por citarem o critério errado seria tão
# incorreto quanto mantê-las sob ele.
# ⚠️ A 0_55 mudou DE NOVO em 2026-08-20: a adoção P-13 fechou as pernas
# julgáveis e desfez o "colapso" (era passo de amostragem) ⇒ voltou a n<6,
# agora com o argumento completo (pernas julgáveis passando). A cadeia
# n<6 → colapso → n<6 está contada na própria entrada dela em _DECLARADAS.

_DECLARADAS = {
    # A declaração da `lu2024_M8_fig14_amp0p25_long` foi REMOVIDA em
    # 2026-08-14: fundava-se no piso do par §3.1.3×Fig.18 (0,0936), e o par é
    # de PROTOCOLOS distintos (ver _EXCECOES_RETRATADAS_LU_PROTOCOLO). A curva
    # volta à fila como indecidível-sem-piso — a fonte não tem réplica da
    # condição no MESMO protocolo.
    # ⇒ RE-DECLARADA algumas horas depois, junto com as outras 7, sob motivo
    #   NOVO e mais forte (ÓRFÃ DE PROTOCOLO, item F) — ver logo abaixo.

    # ── ITEM F (assinado em bloco pelo professor, 2026-08-14; prereg
    # `2026-08-14-item-F-orfas-de-protocolo-prereg.md`): ÓRFÃS DE PROTOCOLO.
    #
    # As 8 formavam a fila form-limited INTEIRA do projeto. Quatro instrumentos
    # independentes, nenhum deles opinião:
    #  1. o PAPER separa os protocolos — §3.1.3 half-sine de MÁQUINA a 1 Hz (as
    #     `fig14_*_long`) × §3.2 controle MANUAL, que o texto diz "eliminar os
    #     efeitos da half-sine" (p.15). Os pares que davam piso cruzavam ensaios
    #     DIFERENTES, e as 5 exceções F7 que repousavam neles foram retratadas;
    #  2. o DADO confirma sem o paper: platô até F/F₀=0,90 dura 27–56 ciclos na
    #     `fig14` e 1 nas `fig18/20`, 3 pares em 3, sempre na mesma direção;
    #     janelas de 1040 × 99 ciclos na "mesma" condição;
    #  3. o MODELO separa as famílias: MAE 3–9× melhor nas `fig18/20`, com a
    #     `fig18_amp0p25` PASSANDO o tripé enquanto a "réplica"
    #     `fig14_amp0p25_long` reprova em 2–5×;
    #  4. a rota de MODELO foi FALSIFICADA por medição
    #     (`lu2024_halfsine_forma_onda_falsificada.md`): "half-sine = metade do
    #     curso" melhora a `amp1p0` em 42 % no fator 0,50 EXATO — e PIORA a irmã
    #     de mesma classe mecânica. Um fato físico não vale numa e não na outra.
    #
    # ⇒ sem rota de modelo, sem rota de piso, sem rota de dado (fonte fechada).
    #
    # ⚠️ DECLARADA ≠ ACERTO DO MODELO. A leitura estrita segue 140/205. O modelo
    # ERRA nestas 8, e erra feio em algumas (`fig14_amp1p0_long` a 9,6× o limite
    # de MAE). Declará-las não conserta nada: retira-as da FILA DE TRABALHO
    # porque o instrumento de validação não as resolve.
    **{c: ("órfã de protocolo (item F, 2026-08-14): a fonte mistura §3.1.3 "
           "half-sine de máquina com §3.2 manual, e não há réplica da condição "
           "no MESMO protocolo — sem rota de modelo (falsificada), de piso "
           "(sem réplica) nem de dado (fonte fechada)")
       for c in (
        "lu2024_M8_fig14_amp0p5_long",
        "lu2024_M8_fig18_amp0p5",
    )},
    # A `lu2024_M8_fig14_amp0p25_long` SAIU em 2026-08-21 — fechou com pacote
    # de LEITURA QUASE PURA (zero fitados); prova em
    # `_DECLARACOES_RETIRADAS_FECHAM_POR_ADOCAO`.
    # A `lu2024_M8_fig14_amp1p0_long` SAIU em 2026-08-21 — a PIOR declarada
    # do projeto (9,6× o MAE) fechou com a forma burst-de-ruptura; prova em
    # `_DECLARACOES_RETIRADAS_FECHAM_POR_ADOCAO`.
    # ⚠️ ERAM 8 — a `lu2024_M8_fig20_T22Nm` SAIU em 2026-08-16 (pico espúrio
    # removido ⇒ mérito; prova em `_DECLARACOES_RETIRADAS_PICO_ESPURIO`); a
    # `lu2024_M8_fig20_T28Nm` (piso lido do terminal publicado), a
    # `lu2024_M8_fig18_amp1p5` (aexp regredido do dado) e a
    # `lu2024_M8_fig20_T16Nm` (floor lido + emb ancorado no c1 publicado)
    # SAÍRAM em 2026-08-20 ⇒ mérito; provas em
    # `_DECLARACOES_RETIRADAS_FECHAM_POR_ADOCAO`.

    # ── DECISÃO (b) do item 8 da mesa, assinada por delegação ("continue",
    # 2026-08-21 16:44): a ÚLTIMA curva da fila form-limited sai por
    # ESGOTAMENTO MEDIDO — 17 estruturas falsificadas com numero (lista enumerada), incluindo
    # a forma desenhada especificamente para a anatomia dela (onset_burst_W,
    # gate próprio do burst: o sino reduz σ 0,0507→0,0271 — a maior redução
    # que a curva já viu — e não fecha; a célula exigiria 6 fitados sem
    # procedência numa curva só, que a regra do projeto proíbe). Anatomia:
    # os 3 gates de estado do engine são monotônicos E compartilhados entre
    # canais; a corcova do miolo (u≈0,2–0,6, +0,063) exige sino desacoplado.
    # A fila de modelo encerra em ZERO. Reabre se: forma nova com
    # procedência, 2ª instância do sino com leitura, ou dado novo da fonte.
    "liu2025_M16_amp0p8":
        "form-limited por ESGOTAMENTO MEDIDO (item 8b, 2026-08-21): 17 "
        "estruturas falsificadas — 8 constantes, rampa (teto σ 0,0283 = "
        "1,13×), t_0-composto, damage em 3 dinâmicas, wear+onset, "
        "graded_scrit, burst compartilhado e burst com gate PRÓPRIO "
        "(σ 0,0507→0,0271 sem fechar, mx 0,11) — σ 0,0419 = 1,68× com "
        "MAE 0,79× e mx 0,86× dentro; prova liu2025_par_de_taxas_opostas.md "
        "§5–§7",

    "zhang2006_fig3_illus_M12x125_20kN_amp0p35":
        "data-limited (proveniência): a Fig. 3 é rotulada 'Illustration of "
        "self-loosening process' — rig do paper ANTERIOR (Jiang 2003/2004), "
        "end-hook desenhado 'kept as drawn' (apparatus_notes/zhang2006.md)",
    # RE-MOTIVADA em 2026-08-07 (P-10 assinada): citava `n<6`, cujo
    # argumento exige que as pernas JULGÁVEIS passem — e o MAE dela erra
    # 2,38×. Mas ela TEM cobertura alternativa válida: o colapso
    # (max|Δdado| > 0,25) com o res.máx a **0 índices** do penhasco.
    # Segue declarada, pelo motivo certo.
    "10_Yang_2023_phenomenological_model__0_55_mm__5":
        "não-julgável: n=5 < 6 pontos na janela — o FLOOR_TRIM=0,10 come o "
        "último ponto (100, 0,05) do CSV de 6 (regra N_MIN_SRES). Motivo "
        "RE-CORRIGIDO em 2026-08-20: a adoção P-13 (prereg ijpem-045-055) "
        "fechou as 2 pernas julgáveis — mae 0,0085, mx 0,0248 — e o "
        "'colapso' de 08-07 era passo de AMOSTRAGEM que a forma cruza a "
        "0,013; o histórico de motivos (n<6 → colapso → n<6) fica: cada "
        "correção citou o critério vigente que a cobria",
    # RE-MOTIVADA em 2026-08-07 (P-10 assinada): citava `n<6` e o MAE dela
    # erra 1,64×. Cobertura alternativa válida: resolução COM a guarda nova
    # — passo 0,2100 e res.máx 0,1600, logo mx/passo = **0,76 ≤ 1**, que é
    # exatamente a condição que a P-10 acrescentou. Segue declarada.
    "10_Yang_2023_phenomenological_model__0_65_mm__6":
        "data-limited (resolução, guarda P-10): mediana |Δdado| = 0,2100 "
        "≥ 0,10 E res.máx 0,1600 ≤ 0,2100 (mx/passo 0,76) — o erro NÃO "
        "excede o passo, então o argumento de amostragem se sustenta. "
        "Motivo CORRIGIDO em 2026-08-07: citava n<6, que não desculpa o "
        "MAE (1,64× o limite)",
    "lu2024_M8_fig20_T4Nm":
        "fora de escopo de junta apertada (P5, professor 2026-07-31): o "
        "próprio paper — 'does not reach the tightening effect' (F₀=2105 N a "
        "4 N·m); degradou em TODA parametrização das rodadas R1/R2 do P3",
    # RETIRADA POR MÉRITO em 2026-08-06 (D-W, campanha MARGENS): a
    # `lu2024_M8_fig18_amp1p5` saiu de _DECLARADAS porque o CSV estava ERRADO,
    # não a métrica — o ponto do argmáximo (N=19, 0,2500) NÃO existia no
    # impresso (27 px acima do único blob verde da coluna) e o desvio era
    # sistêmático (+0,021..+0,035 em x=10–70), com a Tabela 8 do PRÓPRIO paper
    # reprovando o CSV vigente (+0,021/+0,025 em c10/c50) e cravando o novo
    # (−0,0003/+0,0002). Re-digitalizada por pixel calibrado (4 âncoras da
    # Tabela 8, resíduos ≤0,0032): 0,0467/0,1046/0,0477 → 0,0314/0,0742/0,0353
    # ⇒ TRIPÉ. O trigger metric-limited (|Δdado| 1º ciclo = 0,50 > 0,25)
    # continua VERDADEIRO — a classificação só importa para quem não passa.
    # Prereg: 2026-08-06-lu2024-amp1p5-redigitize; extração preservada em
    # vector_extractions/lu2024_fig18a_amp1p5_pixel.json.
    # RETIRADA em 2026-08-10 (prereg 2026-08-10-yang2019-tripe, rodadas 1+5):
    # a `yang2019_M10_amp0p6_5Hz` ENTROU NO TRIPÉ por mérito
    # (0,0158/0,0394/0,0190) com o trim F6 (janela ≤4800, colapso terminal
    # fora da métrica) + N_emb=1000 (relógio do rig). O trigger da declaração
    # (Δdado>0,25 entre pontos) continua VERDADEIRO no dado CRU, mas o
    # colapso está fora da janela julgada — mesmo padrão da lu2024 amp1p5
    # acima: a classificação só importa para quem não passa. Registro da
    # P-12 (2026-08-07) preservado no bloco abaixo.
    # DECLARADA em 2026-08-07 — **P-12 ASSINADA**. Ela chegou aqui vindo da
    # camada de EXCEÇÃO: a P-11 retirou a F5 de *scatter* dela (res.máx
    # 0,3965 > desvio-à-mediana 0,349 da família fig8). Mas o critério de
    # COLAPSO a cobre, e pelo mesmo teste que validou as outras três:
    #     salto 0,264 @índice 23 · res.máx @índice 24 · distância **1**
    # (`Yang2023 0,45` e `yang2019_amp0p6_5Hz` também estão a 1). E a
    # `Yang2023 0,50`, que caiu na MESMA retratação, **falha** este teste
    # (distância 3) e segue sem estatuto — o que mostra que ele discrimina.
    # Princípio aplicado: uma declaração vale se QUALQUER critério assinado a
    # cobre; deixá-la sem estatuto seria sub-classificá-la.
    # test1 RETIRADA em 2026-08-20 — fechou por mérito com o limiar do
    # espectro por espécime (prova em _DECLARACOES_RETIRADAS_FECHAM_POR_ADOCAO).
    # 0_45_mm__4 RETIRADA em 2026-08-20 — fechou por mérito com o pacote
    # P-13 (prova em _DECLARACOES_RETIRADAS_FECHAM_POR_ADOCAO).
    # yang2023ame_axial RETIRADA em 2026-08-20 — fechou por mérito (prova em
    # _DECLARACOES_RETIRADAS_FECHAM_POR_ADOCAO); o diagnóstico da declaração
    # estava invertido (era o MODELO que despencava por emb default).
    # 0_30_mm__8 e 0_35_mm__3 RETRATADAS em 2026-08-07 (P-10 ASSINADA) —
    # ver _DECLARACOES_RETRATADAS_P10. As duas citavam "data-limited por
    # resolução", cujo argumento exige erro DA ORDEM do passo; elas erram
    # 1,22× e 4,00× o passo, e nenhum outro critério assinado as cobre.
    "10_Yang_2023_phenomenological_model__0_15_mm_below_threshold__7":
        "não-julgável: n=4 < 6 pontos na janela — σ_res sem suporte "
        "(regra N_MIN_SRES assinada 2026-08-01, prereg n-minimo-sres; "
        "as 2 pernas julgáveis passam — mae 0,007, mx 0,015 — mas a "
        "afirmação de tripé exige as três; reabre com dado denso)",
    "10_Yang_2023_phenomenological_model__0_50_mm__9":
        "não-julgável: n=5 < 6 pontos na janela — o FLOOR_TRIM=0,10 come o "
        "último ponto (50, 0,02) do CSV de 6 (regra N_MIN_SRES assinada "
        "2026-08-01; aplicada 2026-08-20 quando a adoção P-13 fechou as 2 "
        "pernas julgáveis — mae 0,0201, mx 0,0359 — e o G5 do prereg previu "
        "159 sem checar o n da janela; a curva entra aqui pelo MESMO estatuto "
        "das 0,15/0,18, não por conveniência: a regra é global e anterior)",
    "10_Yang_2023_phenomenological_model__0_18_mm_below_threshold__1":
        "não-julgável: n=5 < 6 pontos na janela — σ_res sem suporte "
        "(regra N_MIN_SRES assinada 2026-08-01; mae 0,008 / mx 0,017 "
        "passam; reabre com dado denso)",
    "zhang19_fig4_1e3cyc_Test1to3_preload_vs_cycles":
        "não-julgável: n=5 < 6 pontos na janela — σ_res sem suporte "
        "(regra N_MIN_SRES assinada 2026-08-01; mae/mx passam com folga; "
        "reabre com dado denso)",
}


def _case_labels() -> Dict[str, dict]:
    """Rótulo MEM POR CASO do error_budget.json (`cases`): {cid: {label,
    evidence, source, family}}. Ausente/ilegível -> {} (degradação honesta)."""
    p = _budget_path()
    if not p.exists():
        return {}
    try:
        b = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    cases = b.get("cases")
    if not isinstance(cases, dict):
        return {}
    # só entradas em forma de dict — o resto do módulo faz .get() nelas
    return {k: v for k, v in cases.items() if isinstance(v, dict)}


def _budget_section(tripe: Optional[Dict[str, bool]] = None) -> str:
    """Orçamento MEM. `tripe` = {case_id: passou no tripé} — quando dado,
    cruza o rótulo com o veredito, porque o rótulo classifica POR MAE
    (evidência do próprio JSON: "mae X <= max(piso+0.02, 0.1)") e sozinho dá
    a impressão de que `no_piso` = resolvido."""
    p = _budget_path()
    if not p.exists():
        return ""
    try:
        b = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ""
    tripe = tripe or {}
    labels = _case_labels()
    # fora-do-tripé por fonte e por rótulo (só para casos que sabemos julgar)
    fora_src: Dict[str, int] = {}
    fora_lab: Dict[str, int] = {}
    for cid, d in labels.items():
        if tripe.get(cid, True):
            continue
        fora_src[d.get("source", "?")] = fora_src.get(d.get("source", "?"), 0) + 1
        lab = d.get("label", "?")
        fora_lab[lab] = fora_lab.get(lab, 0) + 1
    hdr = "".join(f"<th>{l}</th>" for l in _BUDGET_LABELS)
    # Este painel NÃO vem de `records` — vem do `error_budget.json`, artefato
    # gerado à parte. Foi por isso que o UFU_LAB sobreviveu aqui depois de ser
    # retirado do documento (o rótulo saía cru, sem o mapa `NICE`, que é o
    # sintoma de "esta tabela tem outra origem"). Filtrar só as LINHAS deixaria
    # o rodapé somando o que a tabela não mostra mais, então os totais são
    # recomputados das linhas que ficaram.
    by_src_doc = {src: d for src, d in b.get("by_source", {}).items()
                  if src not in _SRC_RETIRADO}
    rows = "".join(
        f'<tr><td>{NICE.get(src, src)}</td>' + "".join(
            f'<td>{d.get(l, 0) or ""}</td>' for l in _BUDGET_LABELS)
        + f'<td class="{"warn" if fora_src.get(src) else ""}">'
          f'{fora_src.get(src, "") or ""}</td></tr>'
        for src, d in sorted(by_src_doc.items()))
    tots = " · ".join(
        f"{l}: <b>{sum(d.get(l, 0) for d in by_src_doc.values())}</b>"
        for l in _BUDGET_LABELS)
    # o alerta que faltava: quantos "no_piso" violam a meta por res.máx
    n_piso_fora = fora_lab.get("no_piso", 0)
    alerta = ""
    if n_piso_fora:
        alerta = (
            f'<p class="alert">O rótulo MEM classifica <b>por MAE</b>. '
            f'Hoje <b>{n_piso_fora}</b> casos rotulados <code>no_piso</code> '
            f'estão <b>FORA do tripé</b> — passam no MAE e violam a meta pelo '
            f'resíduo máximo. Ler "no_piso" como "resolvido" superestima o '
            f'progresso; o número da meta é o do chip <i>no tripé</i>.</p>')
    return (f'<h2>Orçamento de erro (MEM) <span class="c">— classificação por '
            f'MAE</span></h2>'
            f'<p class="sub2">classificação auditável ANTES de mexer '
            f'(metodologia 2026-07-10): {tots}</p>{alerta}'
            f'<div class="ovx"><table class="idx"><thead><tr><th>fonte</th>{hdr}'
            f'<th>fora do tripé</th>'
            f'</tr></thead><tbody>{rows}</tbody></table></div>')


def _ledger_section(n_store: Optional[int] = None,
                    mae_store: Optional[float] = None,
                    rmse_store: Optional[float] = None) -> str:
    """`n_store`/`mae_store` = censo VIGENTE deste documento. Quando dados, a
    seção carimba a DEFASAGEM do ledger: ele só é reescrito quando a campanha
    anexa uma entrada, então pode estar medindo outra régua (outro N, outra
    data) — sem o carimbo a página mostra dois "MAE médio" sem explicação.

    `rmse_store` = RMSE médio de HOJE (3ª régua, 2026-07-29). Existe porque o
    ledger **não tem** a régua nova em nenhuma das entradas antigas e não é
    backfillável; sem este carimbo a curva de RMSE apareceria vazia sem
    explicar por quê."""
    p = repo_root() / "New_Theory" / "convergence_ledger.json"
    if not p.exists():
        return ""
    try:
        led = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ""
    if not isinstance(led, list) or len(led) < 2:
        return ""
    # Reguas na mesma linha do tempo (pergunta do professor 2026-07-11 +
    # historico pedido 2026-07-14): ate #33 o ledger media a fronteira
    # EXPERIMENTAL da campanha (galeria, melhor config por caso); da #34 em
    # diante mede o CANONICO adotado (regra MEM Etapa 0); ingestoes que mudam
    # o N de comparaveis (ex. #48: 114->178 c/ R4) abrem NOVA serie — o salto
    # e troca de regua (casos novos sem fit), nao regressao do modelo.
    # Formato pedido pelo professor (2026-07-15): grafico 1 = MAE MEDIO (nao
    # mediano) +- desvio padrao dos MAEs; grafico 2 = res.max medio +- desvio
    # padrao. mae_std/maxerr_mean/maxerr_std existem de #48 em diante
    # (backfill via git dos estados historicos do store); a media do MAE
    # existe em TODAS as entradas (campo mean).
    # UM gráfico só (2026-07-27): as duas métricas na mesma escala, σ como
    # faixa, réguas marcadas no eixo, valores rotulados na ponta. Ver o
    # docstring de _svg_ledger para por que os 2 gráficos anteriores eram
    # ilegíveis (3 séries de legenda por régua; σ/res.máx só nas 12 últimas).
    chart = _svg_ledger(led)
    chart_ab = ""
    # tabela de marcos (entradas canonicas c/ nota) — historico auditavel
    rows = "".join(
        f'<tr><td>#{i}</td><td>{str(e.get("ts", ""))[:10]}</td>'
        f'<td>{e.get("n", "")}</td>'
        f'<td>{float(e.get("mean", 0)):.4f}</td>'
        f'<td>{"" if e.get("mae_std") is None else f"{float(e['mae_std']):.4f}"}</td>'
        f'<td>{"" if e.get("maxerr_mean") is None else f"{float(e['maxerr_mean']):.4f}"}</td>'
        f'<td>{e.get("n_above_bound", "")}</td>'
        f'<td>{_esc.escape(str(e.get("note", ""))[:220])}</td></tr>'
        for i, e in enumerate(led, 1)
        if e.get("basis", "").startswith("canonico") and e.get("note"))
    marcos = (f'<details><summary>marcos do histórico (entradas canônicas '
              f'com nota)</summary><div class="ovx"><table class="idx">'
              f'<thead><tr><th>#</th><th>data</th><th>n</th><th>MAE médio</th>'
              f'<th>σ(MAE)</th><th>res.máx médio</th>'
              f'<th>&gt;0.10</th><th>nota</th></tr></thead>'
              f'<tbody>{rows}</tbody></table></div></details>') if rows else ""
    last = led[-1]
    mxm_txt = (f' · res.máx médio {float(last["maxerr_mean"]):.4f} '
               f'(σ {float(last["maxerr_std"]):.4f})'
               if last.get("maxerr_mean") is not None else "")
    # A4: carimbo de defasagem — o ledger pode estar noutra régua que a página.
    defas, n_led = "", last.get("n")
    if n_store is not None and n_led is not None and int(n_led) != int(n_store):
        med = (f' e MAE médio {float(last.get("mean", 0)):.4f} contra '
               f'{mae_store:.4f} aqui' if mae_store is not None else "")
        defas = (f'<p class="alert">Esta seção está numa <b>régua diferente</b> '
                 f'da do resto do documento: a última entrada '
                 f'(#{len(led)}, {str(last.get("ts", ""))[:10]}) mede '
                 f'<b>{n_led}</b> casos{med}; o documento mede '
                 f'<b>{n_store}</b>. O ledger só muda quando a campanha anexa '
                 f'uma entrada — anexe uma a cada re-carimbo do store para as '
                 f'duas réguas voltarem a coincidir.</p>')
    prim = next((float(e["mean"]) for e in led if e.get("mean") is not None), 0.0)
    ult = float(last.get("mean", 0) or 0.0)
    i_mx = next((i for i, e in enumerate(led, 1)
                 if e.get("maxerr_mean") is not None), None)
    i_rsd = next((i for i, e in enumerate(led, 1)
                  if e.get("median_resid_std") is not None), None)
    n_rms_led = sum(1 for e in led if e.get("rmse_mean") is not None)
    i_cn = next((i for i, e in enumerate(led, 1)
                 if str(e.get("basis", "")).startswith("canonico")), None)
    queda = (1 - ult / prim) * 100 if prim else 0.0
    ex_led = _explica(
        "Como o erro global caminhou ao longo da campanha — e sob quais "
        "réguas, porque elas mudaram no meio do caminho.",
        [("eixo x", f"índice da entrada do ledger (#1 a #{len(led)}) — é a "
                    f"ordem cronológica das adoções, <b>não</b> tempo linear: "
                    f"entradas vizinhas podem estar a dias ou a minutos"),
         ("eixo y", f"erro médio sobre TODAS as curvas daquela entrada "
                    f"({_UNI})"),
         ("curva MAE", "média do erro médio por curva"),
         ("curva res.máx", f"média do maior desvio pontual por curva; só "
                           f"existe de #{i_mx} em diante (backfill via git do "
                           f"store), por isso começa no meio"),
         ("curva RMSE", "a <b>3ª régua</b> (2026-07-29). Nasce <b>vazia</b> e "
                        "com razão: cada entrada do ledger é um agregado "
                        "escrito na época, os stores daquelas datas não existem "
                        "mais e agregado não se recompõe — a série começa na "
                        "próxima entrada anexada. O valor de hoje está no "
                        "rodapé desta seção"),
         ("curva σ_res", f"a parte <b>oscilante</b> do mesmo RMSE — mediana do "
                         f"desvio-padrão dos resíduos assinados. Existe de "
                         f"#{i_rsd} em diante. Vale a identidade "
                         f"<code>RMSE² = viés² + σ_res²</code>: com as duas "
                         f"curvas no ar, a distância entre elas é o viés"),
         ("faixa sombreada", "±1 desvio-padrão <b>entre curvas</b> — mede a "
                             "dispersão do conjunto, não a incerteza da média"),
         ("linha tracejada vermelha", f"a meta, {META:.2f}"),
         ("área cinza à esquerda", f"régua experimental (galeria, melhor "
                                   f"config por caso), de #1 a #{(i_cn or 1) - 1}"),
         ("marcas verticais", "troca de régua canônica, com o n de casos "
                              "comparáveis daquele trecho"),
         ("rótulo na ponta", "último valor de cada curva")],
        "Compare valores <b>só dentro do mesmo trecho de régua</b>. O degrau "
        "ao cruzar uma marca vertical é entrada de casos novos ainda sem "
        "tratamento — troca de régua, não regressão do modelo. A faixa "
        "estreitando significa que as curvas estão ficando parecidas entre "
        "si; a linha caindo, que o erro típico caiu.",
        f"De #1 a #{len(led)} o MAE médio foi de {prim:.4f} para {ult:.4f} — "
        f"{'queda' if ult < prim else 'alta'} de {abs(queda):.0f}%. "
        f"Repare que a média está <b>abaixo</b> da meta "
        f"{META:.2f} há muitas entradas enquanto dezenas de curvas ainda a "
        f"violam individualmente: a média é indicador de tendência, "
        f"<b>não</b> da meta. Quem mede a meta é o painel "
        f"&laquo;Onde está o erro&raquo; acima.")
    rms_txt = (f' A <b>3ª régua (RMSE)</b> tem {n_rms_led} entrada(s) no '
               f'ledger'
               + (f' — o valor de hoje é <b>{rmse_store:.4f}</b>, e ele entra '
                  f'na série na próxima entrada anexada.'
                  if rmse_store is not None and not n_rms_led else '.')
               + (f' A parte oscilante dela (σ_res) já tem história de '
                  f'#{i_rsd} em diante.' if i_rsd else ''))
    return (f'<h2>Convergência (ledger) — histórico do fit global</h2>'
            f'<p class="sub2"><b>MAE médio</b>, <b>res.máx médio</b>, '
            f'<b>RMSE</b> e <b>σ_res</b> na mesma escala (mesma unidade '
            f'F/F₀), com a faixa <b>±σ</b> sombreada em volta das duas '
            f'primeiras. σ e res.máx só existem de #48 em diante '
            f'(backfill via git do store) — por isso a curva de res.máx começa '
            f'no meio.{rms_txt} Trocas de régua marcadas no eixo; passe o '
            f'mouse num ponto para ver a entrada e o valor.</p>'
            f'{defas}{chart}{chart_ab}{ex_led}{marcos}'
            f'<p class="sub2">Réguas: até #33 mediu-se a fronteira '
            f'experimental da campanha (melhor config por caso, subconjunto '
            f'da galeria); de #34 em diante mede-se o CANÔNICO adotado '
            f'(regra MEM Etapa 0); mudanças de N (ex. #48: 114→178 com a '
            f'Rodada 4) abrem série própria — o degrau entre séries é troca '
            f'de régua (casos novos ainda sem tratamento), não regressão. '
            f'Última (#{len(led)}): MAE médio {float(last.get("mean", 0)):.4f} '
            f'(σ {float(last.get("mae_std", 0)):.4f}){mxm_txt} · '
            f'{_esc.escape(str(last.get("note", ""))[:160])}</p>')


def _explica(o_que: str, variaveis, como: str, hoje: str) -> str:
    """Bloco de explicação de um gráfico, embutido na página.

    REGRA DO PROJETO (2026-07-27, pedido do professor): TODO gráfico deste
    documento carrega uma explicação de ponta a ponta — o que ele responde,
    o que é CADA VARIÁVEL (eixos, marcas, cores, unidades), como ler e o que
    o dado diz hoje. Os números da "leitura de hoje" são SEMPRE calculados do
    store no momento da geração; nunca prosa fixa, senão a explicação mente
    na primeira vez que o gráfico for atualizado."""
    vs = "".join(f'<li><b>{k}</b> — {v}</li>' for k, v in variaveis)
    return (f'<div class="explica">'
            f'<p class="ex-q">{o_que}</p>'
            f'<p class="ex-h">Variáveis</p><ul>{vs}</ul>'
            f'<p class="ex-h">Como ler</p><p>{como}</p>'
            f'<p class="ex-h">Leitura de hoje</p><p>{hoje}</p></div>')


_UNI = ("adimensional: fração da pré-carga, F/F₀ — 1,0 é o aperto intacto e "
        "0 é a junta solta")


def _svg_ledger(led, w: int = 560, h: int = 300) -> str:
    """Histórico do fit num ÚNICO gráfico legível.

    Substitui os 2 gráficos anteriores, que eram difíceis de ler por
    construção: cada régua virava 3 entradas de legenda (média, +σ, −σ), dando
    ~10 séries; e como `maxerr_mean`/`mae_std` só existem nas 12 últimas de 59
    entradas, o segundo gráfico aparecia quase vazio sem explicar por quê.

    Aqui: as duas métricas dividem o mesmo eixo (são a mesma unidade, F/F₀),
    σ vira FAIXA sombreada em vez de linha com nome, as trocas de régua são
    marcadas no próprio eixo e o valor de cada curva é rotulado na ponta —
    nada de legenda para decorar."""
    if not led or len(led) < 2:
        return ""
    n_e = len(led)
    ML, MR, MT, MB = 46, 104, 30, 40
    mae = [e.get("mean") for e in led]
    mstd = [e.get("mae_std") for e in led]
    mxm = [e.get("maxerr_mean") for e in led]
    mxs = [e.get("maxerr_std") for e in led]
    # 3ª régua no histórico (2026-07-29). Duas séries, e a diferença entre elas
    # é a razão de existirem: `rmse_mean` é a régua nova e o ledger NÃO a tem em
    # nenhuma das entradas antigas (não é backfillável — cada entrada é um
    # agregado escrito na época, e os stores daquelas datas não existem mais),
    # então ela nasce vazia e começa a acumular na próxima entrada anexada;
    # `median_resid_std` é a parte OSCILANTE do mesmo RMSE e já está gravada de
    # #47 em diante, então dá história de verdade hoje.
    rms = [e.get("rmse_mean") for e in led]
    rsd = [e.get("median_resid_std") for e in led]
    vals = [float(v) for v in (mae + mxm + rms + rsd) if v is not None]
    if not vals:
        return ""
    hi = max(vals + [META]) * 1.15
    X = lambda i: ML + (i - 1) / max(n_e - 1, 1) * (w - ML - MR)
    Y = lambda v: MT + (1 - min(float(v), hi) / hi) * (h - MT - MB)
    out = []
    # trocas de régua: só as canônicas ganham marca (as experimentais mudam de
    # n várias vezes e poluiriam sem informar)
    marcos, prev = [], None
    for i, e in enumerate(led, 1):
        key = (str(e.get("basis", "")).startswith("canonico"), e.get("n"))
        if key != prev:
            marcos.append((i, key[0], e.get("n")))
            prev = key
    i_canon = next((i for i, c, _ in marcos if c), None)
    if i_canon and i_canon > 1:               # região de régua experimental
        out.append(
            f'<rect x="{ML}" y="{MT}" width="{X(i_canon) - ML:.1f}" '
            f'height="{h - MT - MB}" style="fill:var(--mut);fill-opacity:.07"/>'
            f'<text x="{(ML + X(i_canon)) / 2:.0f}" y="{MT - 8}" '
            f'text-anchor="middle" class="tk" style="fill:var(--mut)">'
            f'régua experimental (galeria)</text>')
    for g in range(5):                        # grade + eixo y
        t = hi * g / 4
        out.append(f'<line x1="{ML}" y1="{Y(t):.1f}" x2="{w - MR}" '
                   f'y2="{Y(t):.1f}" class="gl"/>'
                   f'<text x="{ML - 6}" y="{Y(t) + 3:.1f}" text-anchor="end" '
                   f'class="tk">{t:.2f}</text>')
    out.append(f'<line x1="{ML}" y1="{Y(META):.1f}" x2="{w - MR}" '
               f'y2="{Y(META):.1f}" class="rl" stroke-dasharray="4 3"/>'
               f'<text x="{w - MR + 4}" y="{Y(META) + 3:.1f}" class="tk" '
               f'style="fill:var(--err)">meta {META:.2f}</text>')
    primeiro = True
    for i, canon, nn in marcos:               # separadores de régua canônica
        if not canon or i <= 1:
            continue
        # só o 1º marco leva a palavra: os canônicos 178/180 ficam a ~57px um
        # do outro e os rótulos longos se sobreporiam
        rot = f"canônico n={nn}" if primeiro else f"n={nn}"
        primeiro = False
        out.append(f'<line x1="{X(i):.1f}" y1="{MT}" x2="{X(i):.1f}" '
                   f'y2="{h - MB}" class="gl" stroke-dasharray="3 3"/>'
                   f'<text x="{X(i) + 3:.1f}" y="{MT - 8}" class="tk" '
                   f'style="fill:var(--mut)">{rot}</text>')

    def _banda(mean, std):
        up, dn = [], []
        for i, (m, s) in enumerate(zip(mean, std), 1):
            if m is None or s is None:
                continue
            up.append((X(i), Y(float(m) + float(s))))
            dn.append((X(i), Y(max(float(m) - float(s), 0.0))))
        if len(up) < 2:
            return ""
        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in up + dn[::-1])
        return (f'<polygon points="{pts}" style="fill:var(--mut);'
                f'fill-opacity:.20"><title>faixa ±σ entre as curvas</title>'
                f'</polygon>')

    def _curva(serie, cor, nome):
        pts = [(X(i), Y(float(v)), i, float(v))
               for i, v in enumerate(serie, 1) if v is not None]
        if not pts:
            return "", ""
        pl = " ".join(f"{x:.1f},{y:.1f}" for x, y, _, _ in pts)
        s = (f'<polyline points="{pl}" fill="none" stroke-width="2.2" '
             f'style="stroke:var(--{cor})"/>')
        s += "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.4" '
                     f'style="fill:var(--{cor})"><title>#{i}: {v:.4f}</title>'
                     f'</circle>' for x, y, i, v in pts)
        lx, ly, _, lv = pts[-1]
        rot = (f'<text x="{lx + 7:.1f}" y="{ly + 4:.1f}" class="tk" '
               f'style="fill:var(--{cor});font-weight:600">{nome} {lv:.3f}'
               f'</text>')
        return s, rot

    out.append(_banda(mae, mstd))
    out.append(_banda(mxm, mxs))
    c1, r1 = _curva(mxm, "warn", "res.máx")
    c2, r2 = _curva(mae, "accent", "MAE")
    c3, r3 = _curva(rms, "good", "RMSE")
    c4, r4 = _curva(rsd, "di", "σ_res")
    out += [c1, c2, c3, c4, r1, r2, r3, r4]
    for g in (1, n_e // 2, n_e):              # eixo x
        out.append(f'<text x="{X(g):.1f}" y="{h - MB + 14}" '
                   f'text-anchor="middle" class="tk">#{g}</text>')
    out.append(f'<text x="{(ML + w - MR) / 2:.0f}" y="{h - 4}" '
               f'text-anchor="middle" class="axl">entrada do ledger</text>'
               f'<text x="13" y="{(MT + h - MB) / 2:.0f}" text-anchor="middle" '
               f'class="axl" transform="rotate(-90 13 '
               f'{(MT + h - MB) / 2:.0f})">erro médio (F/F₀)</text>')
    return (f'<svg viewBox="0 0 {w} {h}" class="plot" role="img" '
            f'aria-label="histórico do erro médio por entrada do ledger">'
            f'{"".join(out)}</svg>')


def _svg_barh(rows, w: int = 560, lw: int = 118, rw: int = 74,
              key: str = "") -> str:
    """Barras horizontais [(rótulo, valor, total)] — SVG puro, sem JS (imprime
    e funciona em file://). Rótulo curto à esquerda, contagem à direita.

    `key` publica a geometria em `data-*` para os controles ao vivo redesenharem
    as barras quando os limites mudam (o conjunto de fontes fora do tripé muda
    com eles)."""
    if not rows:
        return ""
    bh, gap = 15, 7
    h = len(rows) * (bh + gap) + 6
    vmax = max(v for _, v, _ in rows) or 1
    out = []
    for i, (lab, v, tot) in enumerate(rows):
        y = i * (bh + gap) + 3
        bl = (w - lw - rw) * v / vmax
        frac = v / tot if tot else 0
        out.append(
            f'<text x="{lw - 6}" y="{y + bh - 3}" text-anchor="end" '
            f'class="tk">{_esc.escape(str(lab))}</text>'
            f'<rect x="{lw}" y="{y}" width="{max(bl, 1.0):.1f}" height="{bh}" '
            f'rx="3" style="fill:var(--warn);fill-opacity:.85"><title>'
            f'{_esc.escape(str(lab))}: {v} de {tot} fora ({frac:.0%})</title>'
            f'</rect>'
            f'<text x="{lw + bl + 6:.1f}" y="{y + bh - 3}" class="tk">'
            f'{v}/{tot}</text>')
    return (f'<svg viewBox="0 0 {w} {h}" class="plot" role="img" '
            f'data-barh="{_esc.escape(key)}" data-lw="{lw}" data-rw="{rw}" '
            f'data-bh="{bh}" data-gap="{gap}" data-w="{w}" '
            f'aria-label="curvas fora do tripé por fonte">{"".join(out)}</svg>')


def _pontos_julgados(result, n_total: Optional[int]) -> str:
    """Diz quantos pontos da curva a métrica de fato pontuou — quando faltam.

    Por que existe (auditoria de 2026-08-16,
    `New_Theory/piso_da_metrica_o_que_ele_esconde.md`): `runner.FLOOR_TRIM` =
    0,10 retira da métrica todo ponto com F/F₀ < 0,10, **e encurta a simulação
    junto**. Em **38 das 205** curvas isso oculta pontos — **662** no total —, e
    a página não dizia nada. Medido no lote (re-simulando com o piso em zero):
    na mediana o erro oculto é **0,86×** o julgado, ou seja o piso é benigno na
    maioria; mas há casos em que ele decide a leitura da página:

    · `lu2024_M8_fig18_amp2p0` **fecha o tripé** com MAE 0,0110 sendo julgada em
      **6 de 13** pontos, e na metade oculta o erro é **6,3×** maior;
    · as duas curvas axiais do `SUN_2025_CRIMP` escondem **um** ponto cada, e é
      o da **fratura** (o dado cai a 0,000 num passo) — ali o piso está
      *correto*, porque essas configs não modelam fratura.

    ⚠️ Por isso o texto NÃO é um aviso de erro: os dois casos acima têm
    interpretações opostas e a página não tem como distinguir. Ele informa a
    cobertura e deixa a leitura para quem sabe da curva.

    ⚠️ **E não atribui a causa, porque medi as causas e são TRÊS** (2026-08-16,
    nas 82 curvas com algum gap): **32** por dado abaixo de 0,10 (`FLOOR_TRIM`),
    **12** por `trim_n_max` declarado de trecho *out-of-model*, **8** por ambos e
    **30** por **efeito de borda** — o último ponto da CSV cai um fio além do
    `n_max` (na `bauer2024_M12_fig8_test1` a CSV vai a N=873 e a métrica para em
    835). A 1ª redação desta linha dizia "porque o dado cai abaixo do piso" e
    estaria **errada em 42 das 82**.

    **Materialidade:** só aparece com **≥ 2 pontos** ocultos **e ≥ 10 %** da
    curva — o que reduz de 82 para **37** e elimina justamente os efeitos de
    borda de 1 ponto, que seriam ruído (e ruído desliga guarda). `n_total is
    None` ou gap imaterial ⇒ string vazia, página bit-idêntica.
    """
    n_ok = len(getattr(result, "metric_x", None) or [])
    if not n_total or not n_ok or n_total <= n_ok:
        return ""
    ocultos = n_total - n_ok
    frac = ocultos / n_total
    if ocultos < 2 or frac < 0.10:
        return ""
    return (f'<p class="sub2"><b>Cobertura da métrica:</b> julgada em '
            f'<b>{n_ok} de {n_total}</b> pontos do dado — {ocultos} '
            f'({100 * frac:.0f}&#8201;%) ficam fora da janela pontuada. As causas '
            f'possíveis são três e a página não adivinha qual é a desta curva: '
            f'dado abaixo do piso de 0,10 (<code>FLOOR_TRIM</code>, que também '
            f'encurta a simulação), <code>trim_n_max</code> declarado de trecho '
            f'fora do modelo (ver §6) ou o último ponto além do <code>n_max</code>. '
            f'Não é aviso de erro: onde a curva termina em <b>fratura</b> o '
            f'descarte está <b>certo</b> — o modelo dessas configs não a modela; '
            f'onde ela apenas <b>decai</b>, o trecho não medido pode esconder '
            f'erro. Medido no lote: na mediana o erro oculto é <b>0,86×</b> o '
            f'julgado, mas numa curva do tripé chega a <b>6,3×</b>. Auditoria: '
            f'<code>New_Theory/piso_da_metrica_o_que_ele_esconde.md</code>.</p>')


def _tripe_block(result, lim_sd: Optional[float] = None,
                 n_total: Optional[int] = None) -> str:
    """§3 — O TRIPÉ DESTA CURVA, perna por perna, e o que o RMSE significa nela.

    Por que existe (auditoria 2026-07-29): a régua virou de duas para três pernas
    naquele dia e o painel mestre foi atualizado, mas **o report por caso não**.
    Ele mostrava `MAE` (pintado de verde contra o limite VELHO de 0,1, não contra
    `META_MAE`=0,05), `erro máx` e um `RMSE` solto — número sem leitura — e
    **nenhuma menção ao σ_res**, que é justamente a perna que passou a decidir.
    Consequência medível: uma curva reprovada no documento mestre abria a própria
    página com o cartão de MAE VERDE. Mesma armadilha do §4.43 (a medição
    envelhece em silêncio), aqui dentro do código.

    O RMSE ganha as duas leituras que ele de fato carrega, e nenhuma é "porta":

    · **posição na cunha** `MAE <= RMSE <= res.máx` (as três normas-p, p=1,2,∞,
      do MESMO vetor de resíduo): perto do MAE = erro espalhado pela curva; perto
      do res.máx = concentrado em picos. Como a desigualdade vale sempre, um
      limite no RMSE nunca reprovaria quem passa no res.máx — seria redundante;
    · **decomposição exata** `RMSE² = viés² + σ_res²`: separa erro de NÍVEL (o
      modelo mora de um lado do dado) de erro de FORMA (cruza e oscila). São
      doenças diferentes e pedem correções diferentes.
    """
    a, b = result.mae, result.maxerr
    # regra n<6 (2026-08-01): sigma nao-julgavel entra como None e o cartao
    # diz isso em vez de fingir uma medicao com 4-5 pontos
    c = sres_para_censo(result)
    if a is None or b is None:
        return ""
    # D1: `lim_sd` = limite EFETIVO da 3ª perna desta FONTE (max(global, piso
    # medido)), passado por quem conhece o conjunto (write_reports). None =
    # global — e com a flag desligada é sempre None, bit-idêntico.
    eff_sd = META_SRES if lim_sd is None else float(lim_sd)
    vies = _bias_of(result)
    sev = _severidade(a, b, c, META_MAE, META_MAX, eff_sd)
    manda = _perna_manda(a, b, c, META_MAE, META_MAX, eff_sd)
    nota_d1 = ""
    if eff_sd > META_SRES:
        nota_d1 = (f' <span class="s3f">(limite por fonte — D1: '
                   f'max({META_SRES:.4g}; piso medido) = {eff_sd:.4g})</span>')
    linhas = []
    for rot, val, lim, chave in (("MAE", a, META_MAE, "mae"),
                                 ("resíduo máximo", b, META_MAX, "mx"),
                                 (f"σ_res{nota_d1}", c, eff_sd, "sd")):
        if val is None:
            linhas.append(
                f'<tr><td>{rot}</td><td>—</td><td>{lim:.4g}</td>'
                f'<td class="warn">não julgável — o registro não tem a métrica '
                f'(store antigo: re-simule)</td></tr>')
            continue
        mult = val / lim
        passa = mult <= 1.0
        marca = ("<b>a perna que manda</b>" if chave == manda
                 else ("passa" if passa else "viola"))
        linhas.append(
            f'<tr><td>{rot}</td><td><b>{val:.4f}</b></td><td>{lim:.4g}</td>'
            f'<td class="{"good" if passa else "warn"}">{mult:.2f}× o limite '
            f'&#183; {marca}</td></tr>')
    _NOME = {"mae": "o MAE", "mx": "o resíduo máximo", "sd": "o σ_res"}
    if manda is None:
        ver = '<span class="good">passa nas três pernas</span>'
    else:
        ver = (f'<span class="warn">fora do tripé</span> — a distância à origem '
               f'é <b>{sev:.2f}×</b> o limite (norma do máximo, a mesma do '
               f'gradiente do 3D no documento mestre), e a perna que manda é '
               f'<b>{_NOME[manda]}</b>')
    # a cunha: onde o RMSE cai entre MAE e res.máx (0 = no MAE, 1 = no pico)
    cunha = ""
    if result.rmse is not None and b > a:
        pos = min(max((result.rmse - a) / (b - a), 0.0), 1.0)
        cunha = (f'<tr><td>posição na cunha</td><td><b>{pos:.2f}</b></td>'
                 f'<td>0…1</td><td>0 = erro <b>espalhado</b> pela curva '
                 f'(RMSE junto do MAE) &#183; 1 = <b>concentrado em picos</b> '
                 f'(RMSE junto do res.máx)</td></tr>')
    dec = ""
    if result.rmse is not None and vies is not None and c is not None:
        frac = (abs(vies) / result.rmse) if result.rmse > 1e-12 else 0.0
        qual = ("quase todo <b>de NÍVEL</b>: o modelo mora de um lado do dado"
                if frac > 0.9 else
                "quase todo <b>de FORMA</b>: o modelo cruza o dado e oscila"
                if frac <= 0.5 else "misto entre nível e forma")
        dec = (f'<tr><td>|viés| / RMSE</td><td><b>{frac:.2f}</b></td>'
               f'<td>0…1</td><td>{qual} &#183; viés {vies:+.4f}, e vale '
               f'<code>RMSE² = viés² + σ_res²</code></td></tr>')
    return (
        f'<div class="tripe"><h3>Veredicto do tripé — perna por perna</h3>'
        f'<p class="sub2">Meta de 2026-07-29: <b>res.máx &le; {META_MAX:.4g}</b> '
        f'E <b>MAE &le; {META_MAE:.4g}</b> E <b>σ_res &le; {META_SRES:.4g}</b> '
        f'(as três, conjunção). {ver}.</p>'
        f'<table class="idx"><thead><tr><th>perna</th><th>valor</th>'
        f'<th>limite</th><th>leitura</th></tr></thead><tbody>{"".join(linhas)}'
        f'</tbody></table>'
        f'{_pontos_julgados(result, n_total)}'
        f'<h4>RMSE {_fnum(result.rmse)} — o que ele diz aqui (não é porta)</h4>'
        f'<p class="sub2">As três normas-p do MESMO resíduo obedecem '
        f'<code>MAE &le; RMSE &le; res.máx</code> sempre, então um limite no '
        f'RMSE nunca reprovaria quem passa no res.máx: seria redundante. O que '
        f'ele carrega é <i>onde</i> o erro está e <i>de que tipo</i> ele é.</p>'
        f'<table class="idx"><thead><tr><th>régua</th><th>valor</th>'
        f'<th>faixa</th><th>leitura</th></tr></thead><tbody>{cunha}{dec}'
        f'</tbody></table></div>')


def _bias_of(res) -> Optional[float]:
    """Viés = média do resíduo **assinado** (modelo − dado) nos MESMOS três
    vetores que a métrica comparou (`metric_pred`/`metric_data`) — nunca
    recomputado de `ratio`, que é a curva amostrada (defeito de 2026-07-27).

    Por que ele importa e o RMSE sozinho não: vale a identidade exata
    `RMSE² = viés² + σ_res²` (verificada nos 203 registros do store, erro
    máximo 1,7e-14). O RMSE MISTURA as duas coisas; separados, cada termo
    responde uma pergunta diferente — `viés` = o modelo está de um lado do
    dado (nível errado, "divergindo"); `σ_res` = o modelo cruza o dado e
    oscila em torno dele (nível certo, forma ruidosa).

    Fallback para registros sem os vetores (store antigo): a mesma identidade
    dá a MAGNITUDE do viés a partir de `rmse`/`resid_std`, mas **não o sinal**
    — por isso é só fallback."""
    mp, md = getattr(res, "metric_pred", None), getattr(res, "metric_data", None)
    if mp and md and len(mp) == len(md):
        return sum(float(p) - float(d) for p, d in zip(mp, md)) / len(mp)
    if res.rmse is not None and res.resid_std is not None:
        v = float(res.rmse) ** 2 - float(res.resid_std) ** 2
        return v ** 0.5 if v > 0 else 0.0
    return None


# Curvas que NUNCA entram em família mecânica automática (erratum ROUSSEAU,
# 2026-08-01): a chave (fonte, δ, F_amp, modo) não vê geometria per-case e
# pareou espessuras DIFERENTES como réplicas. Pares declarados seguem válidos.
# Campos de INPUT que entram na identidade da condição (prereg
# `2026-08-23-chave-estendida-pareamento`). São as variáveis que os papers VARREM,
# lidas do `case_id` por `validation_cases._varredura_por_curva`. Antes delas a
# chave dizia "mesma condição" para curvas que diferem em carga axial, grip,
# rugosidade, espessura, remontagem ou espécime — e foi dessa cegueira que saíram
# SETE retratações de exceção (axial do ECCLES, grip do ICMEZ, rugosidade do CHU,
# protocolo do LU, espessura do ROUSSEAU, condições do CACCESE, e o teste de
# premissa F5 lendo a `eccles fig7` como "ensemble de 4 réplicas").
# ⚠️ Ordem e conteúdo são parte da chave: acrescentar campo aqui MUDA o piso
# medido, logo muda `limite_sres`, logo pode mover o censo. Não é lista de
# conveniência — é prereg.
_CAMPOS_VARRIDOS = (
    "axial_force_amplitude_N",   # LIU_2016 af7p5..12p5kN ; LIU_2017_AXIAL
    "roughness_Ra_um",           # LI_2022_MARSTRUC Ra0p078..0p8 ; CHU Ra1p6um
    "grip_length_mm",            # ICMEZ_2025 lk13p8 / lk19p8
    "member_thickness_mm",       # ROUSSEAU_2025 t10 / t12 / t14
    "reassembly_count",          # SUN_2025_REASSY reassy02..10
    "specimen_label",            # material/ambiente, geometria, posição, graxa×porca
    "external_axial_N",          # ECCLES_2010 0,7..4,0 kN
    "external_axial_mode",       # constant × intermittent
    # ⚠️ AJUSTADA, nao ALCANCADA — e' essa a regra de admissao nesta tupla
    # (prereg `2026-08-23-fecha-tickets-e-dedup`). `frequency_Hz` e' ajustada:
    # duas replicas na mesma frequencia nominal tem o mesmo valor, e medido ela
    # quebra ZERO pares existentes (225 -> 225). `initial_preload_N` seria
    # ALCANCADA e esta FALSIFICADA: o `_PARES_REPLICA_DECLARADOS` existe porque
    # "aperto nunca repete" (4-14% nos pares do LU), logo toda replica real tem
    # F0 diferente e por-lo aqui destruiria pareamento legitimo em todo o projeto.
    "frequency_Hz",              # LI_2022_TRIBOINT 10/15/20 Hz
)

# Fontes em que a CHAVE ESTENDIDA já distingue tudo o que a lista manual
# bloqueava — nelas o bloqueio é SUPERSEDIDO POR MECANISMO e deixa de ser
# aplicado. As entradas ficam em `_SEM_FAMILIA_MECANICA` porque os motivos
# escritos são PROCEDÊNCIA: eles registram por que o pareamento era falso, e
# apagá-los perderia a razão de o mecanismo existir.
#
# Medido (prereg §4, P1–P4): pareamento espúrio 74 → 24 curvas; as 24 que restam
# são pareamentos CORRETOS (réplicas reais, repetição do autor, mesmo ensaio em 2
# figuras, baselines de mesma condição) mais as 14 dos 3 tickets abaixo. Censo
# **inalterado** (0 entram, 0 saem) e nenhum limite afrouxa — o único que se move
# é o do `ECCLES_2010`, que APERTA (0,0698 → 0,0565).
#
# ⚠️ NÃO estão aqui as três fontes cuja variável varrida o registry TEM mas a
# chave ainda não lê — `KARLSEN_2022` (dispositivo de travamento),
# `LI_2022_MARSTRUC` (pré-carga) e `LI_2022_TRIBOINT` (frequência). São 14 curvas
# e um passo separado: `frequency_Hz`/`initial_preload_N` entram na chave de TODA
# fonte, não só das três, logo mudam pareamento onde ele hoje está certo.
_FONTES_RESOLVIDAS_POR_CHAVE = frozenset({
    "CACCESE_2009", "CHU_2026", "ECCLES_2010", "ICMEZ_2025", "JCSR_2023",
    "LIU_2016", "LU_2024", "QIN_2024", "ROUSSEAU_2025", "SUN_2025_CRIMP",
    "YANG_2021",
    # Fechados em 2026-08-23 (prereg `fecha-tickets-e-dedup`), com o campo que
    # resolveu cada um: `LI_2022_TRIBOINT` pela `frequency_Hz` (10/15/20 Hz);
    # `KARLSEN_2022` pelo rotulo de TRAVAMENTO (hv x hvtorqued x vibralock x
    # vibralock_torqued — `run21p0` e `run29p0` tem F0 identico e so o
    # dispositivo os separa); `LI_2022_MARSTRUC` pelo rotulo de pre-carga
    # NOMINAL (5/10/15 kN). Com isto o bloqueio ATIVO vai a ZERO.
    "KARLSEN_2022", "LI_2022_MARSTRUC", "LI_2022_TRIBOINT",
})

_SEM_FAMILIA_MECANICA = {
    # ICMEZ_2025 (2026-08-14, audit `icmez_chave_cega_ao_grip.md`, executado
    # por delegação "assine e continue em loop"): a chave mecânica é CEGA ao
    # `grip_mm` e as 4 famílias pareavam comprimentos de aperto 13,8 × 19,8 mm
    # — rigidezes de junta diferentes (MAE de piso 0,105–0,209 = diferença de
    # grip, não repetibilidade; mesma assinatura de SUN/KARLSEN/ROUSSEAU, já
    # bloqueados). 5ª invalidação de pareamento. Custo declarado: censo −5;
    # 3 das 8 sobrevivem por mérito (σ ≤ 0,025 sem piso).
    "demir2024_amp0p3_F14p3_lk13p8": "grip 13,8 ≠ 19,8 mm — rigidez varrida",
    "demir2024_amp0p3_F14p3_lk19p8": "grip 19,8 ≠ 13,8 mm — rigidez varrida",
    "demir2024_amp0p3_F17p6_lk13p8": "grip 13,8 ≠ 19,8 mm — rigidez varrida",
    "demir2024_amp0p3_F17p6_lk19p8": "grip 19,8 ≠ 13,8 mm — rigidez varrida",
    "demir2024_amp0p4_F14p3_lk13p8": "grip 13,8 ≠ 19,8 mm — rigidez varrida",
    "demir2024_amp0p4_F14p3_lk19p8": "grip 19,8 ≠ 13,8 mm — rigidez varrida",
    "demir2024_amp0p4_F17p6_lk13p8": "grip 13,8 ≠ 19,8 mm — rigidez varrida",
    "demir2024_amp0p4_F17p6_lk19p8": "grip 19,8 ≠ 13,8 mm — rigidez varrida",
    # CHU_2026 (2026-08-14, mesmo audit): a família δ=0,5 pareava
    # `Ra1p6um_test9` (Ra 1,6 µm) com `test3` (Ra 0,4) porque o CONFIG usa a
    # rugosidade default nas duas (dívida do item B da fila) — a média das
    # famílias inflava o limite da fonte (0,0507) e o `test5`, da família
    # LEGÍTIMA (test5×test6_repeat, "Réplica do test5" na nota), passava por
    # causa da ilegítima. Bloqueio cirúrgico só no test9; a δ=1,0 fica.
    # Custo declarado: censo −1 (test5). A dívida de INPUT segue no item B.
    "chu2026ti_D0p5mm_F0_49kN_Ra1p6um_test9": (
        "Ra 1,6 µm ≠ 0,4 µm — rugosidade é a variável varrida"),
    # LU_2024 §3.1.3 (2026-08-14): as 3 corridas longas são half-sine de
    # MÁQUINA a 1 Hz; as Fig.18/20 são controle MANUAL (§3.2) — protocolos
    # distintos pelo próprio paper ⇒ nunca parear com as nominais.
    "lu2024_M8_fig14_amp0p25_long": "protocolo ≠ (half-sine 1Hz × manual §3.2)",
    "lu2024_M8_fig14_amp0p5_long": "protocolo ≠ (half-sine 1Hz × manual §3.2)",
    "lu2024_M8_fig14_amp1p0_long": "protocolo ≠ (half-sine 1Hz × manual §3.2)",
    "rousseau2025_steel_t10": "t=10mm ≠ t=12mm — espessura é a variável varrida",
    "rousseau2025_steel_t12": "t=12mm ≠ t=10mm — espessura é a variável varrida",
    # Fig. 6: aço e HDPE na MESMA condição (0,2 mm, 3,5 kN) — a chave só não
    # os pareia porque o F_amp difere em 1,6 N (sorte, não desenho); materiais
    # diferentes jamais são réplicas um do outro.
    "rousseau2025_steel_t10_amp0p2": "material ≠ do par (aço × HDPE)",
    "rousseau2025_hdpe_t10_amp0p2": "material ≠ do par (HDPE × aço)",
}
# 3ª ocorrência da MESMA classe no dia (prereg 2026-08-01-familias-falsas):
# em casos AXIAIS/CREEP δ=0 **e** F_amp=0, então a chave mecânica joga a
# fonte INTEIRA numa família só e o "piso" vira dispersão ENTRE CONDIÇÕES.
# Medido: JCSR_2023 (5 AMBIENTES: indoor/outdoor/seawater/galv/inox) impunha
# σ 0,2214 = 8,9× o limite global, e CACCESE_2009 (7 condições distintas)
# impunha 0,0270. As curvas abaixo nunca são pareadas automaticamente; o
# ÚNICO par legítimo do CACCESE (tapered rep1↔rep2, mesma condição) entra
# por `_PARES_REPLICA_DECLARADOS`. LI_2022_MARSTRUC e QIN_2024 têm o mesmo
# defeito de chave mas piso < global (o `max` já os torna inócuos) — ficam
# listados assim mesmo, porque "inócuo hoje" não é "correto".
_SEM_FAMILIA_MECANICA.update({
    cid: motivo for cid, motivo in (
        ("jcsr2023_plain_indoor", "ambiente ≠ (chave cega: δ=F=0)"),
        ("jcsr2023_plain_outdoor", "ambiente ≠ (chave cega: δ=F=0)"),
        ("jcsr2023_plain_seawater", "ambiente ≠ (chave cega: δ=F=0)"),
        ("jcsr2023_galv_seawater", "revestimento+ambiente ≠ (chave cega)"),
        ("jcsr2023_stainless_seawater", "material+ambiente ≠ (chave cega)"),
        ("caccese2009_compblock_34kPa", "condição ≠ (chave cega: δ=F=0)"),
        ("caccese2009_compblock_71kPa", "condição ≠ (chave cega: δ=F=0)"),
        ("caccese2009_protruding_45kN", "geometria ≠ (chave cega)"),
        ("caccese2009_retighten_12p7mm_no_retighten", "grip ≠ (chave cega)"),
        ("caccese2009_retighten_19p1mm_no_retighten", "grip ≠ (chave cega)"),
        ("caccese2009_tapered_45kN_rep1", "só pareia com rep2 (par declarado)"),
        ("caccese2009_tapered_45kN_rep2", "só pareia com rep1 (par declarado)"),
        ("li2022marstruc_creep_10kN_Ra0p8_min", "rugosidade ≠ (chave cega)"),
        ("li2022marstruc_creep_10kN_Ra0p078_min", "rugosidade ≠ (chave cega)"),
        ("li2022marstruc_creep_10kN_Ra0p122_min", "rugosidade ≠ (chave cega)"),
        ("li2022marstruc_creep_10kN_Ra0p306_min", "rugosidade ≠ (chave cega)"),
        ("li2022marstruc_creep_5kN_Ra0p8_min", "pré-carga ≠ (chave cega)"),
        ("li2022marstruc_creep_15kN_Ra0p8_min", "pré-carga ≠ (chave cega)"),
        ("qin2024acm_25C_i0pct", "corrente ≠ (chave cega)"),
        ("qin2024acm_25C_i0p6pct", "corrente ≠ (chave cega)"),
        ("qin2024acm_25C_i1p2pct", "corrente ≠ (chave cega)"),
    )})
# 4ª ocorrência da MESMA classe (2026-08-05, medição na Fig. 8 do paper): no
# LI_2022_TRIBOINT a variável varrida é a **FREQUÊNCIA** (10/15/20 Hz) e ela
# **não está na chave** ⇒ as 4 curvas caíam numa família só e **5 dos 6 pares
# cruzavam frequências**. Piso falso medido: MAE 0,0413 · máx 0,0590 ·
# σ 0,0117. O Único par de mesma condição (`axialmin_10Hz` × `axial_10Hz_full`,
# Fig. 8c × Fig. 8a) entra DECLARADO e mede MAE 0,0315 · máx 0,0655 ·
# σ 0,0083. Inócuo no censo (os dois pisos ficam < 0,025 ⇒ `limite_sres`
# = 0,0250 antes e depois), mas "inócuo hoje" não é "correto" — mesma regra
# aplicada ao MARSTRUC/QIN acima.
# A hipótese "as duas são o **MESMO ensaio em duas figuras**" — que mudaria o
# DENOMINADOR via `_CID_NAO_COMPARAVEL`, precedente LU fig18_amp1p0≡fig20_T22Nm
# — foi levantada (concordam a 0,5 % em força ABSOLUTA em N=2e5) e
# **FALSIFICADA por medição** no mesmo dia (`fila_form_limited_3_anatomia.md`
# §3): nenhuma atribuição de base faz as trajetórias absolutas coincidirem (o
# fator de escala ótimo B→A é **1,0234**, não 1,0435 = 12,0/11,5, e sobram
# **0,112 kN de FORMA** depois de escalar), a convergência 4,2 %→0,5 % é
# **monótona** — assinatura de dois F₀ distintos sob a MESMA carga imposta, que
# em modo FORÇA fixa a força residual independentemente de F₀ — e a Fig. 12
# plota **3 espécimes** a 10 Hz (vidas 2,87/3,58/4,16 ×10⁵). ⇒ são espécimes
# DISTINTOS, o denominador fica em 205 e o par é piso de REPETIBILIDADE.
_SEM_FAMILIA_MECANICA.update({
    cid: motivo for cid, motivo in (
        ("li2022ti_axial_10Hz_full", "frequência ≠ (chave cega); só pareia com "
                                     "axialmin_10Hz (par declarado)"),
        ("li2022ti_axialmin_10Hz", "frequência ≠ (chave cega); só pareia com "
                                   "axial_10Hz_full (par declarado)"),
        ("li2022ti_axialmin_15Hz", "frequência ≠ (chave cega: 15 ≠ 10/20 Hz)"),
        ("li2022ti_axialmin_20Hz", "frequência ≠ (chave cega: 20 ≠ 10/15 Hz)"),
        # RISCO LATENTE fechado no mesmo commit (achado da investigação do piso
        # do ROUSSEAU, 2026-08-05): `hdpe_t10` e `hdpe_t12` só ficavam fora de
        # uma família FALSA pela diferença **0,5 vs 0,49 mm** da Tabela 2 — a
        # proteção era ACIDENTAL, igual aos "1,6 N" do par amp0p2 acima.
        # Arredondar esse delta (ou re-digitalizar e re-registrar a amplitude)
        # ressuscitaria o defeito que o erratum de 2026-08-01 corrigiu.
        # Efeito HOJE: **zero** (a fonte não tem família automática nenhuma) —
        # é bloqueio declarativo, e é por isso que entra ANTES da
        # re-digitalização (D-R), não depois.
        ("rousseau2025_hdpe_t10", "espessura ≠ (chave cega); só 0,5≠0,49 mm "
                                  "separava do t12 — proteção acidental"),
        ("rousseau2025_hdpe_t12", "espessura ≠ (chave cega); só 0,49≠0,5 mm "
                                  "separava do t10 — proteção acidental"),
    )})
# 5ª ocorrência da MESMA classe (2026-08-06, sonda de pixel da campanha
# FAXINA-E-ANATOMIA): no LIU_2016 a chave cega juntava **n=10** curvas numa
# família só — a varredura de TORQUE inteira (fig9a m30..m50), a fig11a af10kn,
# a de LUBRIFICAÇÃO (fig13a dry E MoS₂!) e as duas corridas da fig7 — porque
# todas têm δ=0 e F_amp idêntico no config. Piso falso medido: MAE 0,1025 ·
# máx 0,1121 · σ 0,0176 = espalhamento de CONDIÇÃO. Inócuo no censo hoje
# (σ do piso falso < 0,025 ⇒ `limite_sres` = 0,0250 antes e depois, 0 curvas
# mudam — medido), mas qualquer F7 futura citando esse piso seria inválida.
# E a família continha os suspeitos de RE-PLOT (fig13a_dry ≡ fig7_run1 por
# prova metrológica — decisão de denominador na fila do professor).
_SEM_FAMILIA_MECANICA.update({
    cid: motivo for cid, motivo in (
        ("liu2016wear_fig9a_m30nm", "torque ≠ (chave cega: varredura M0)"),
        ("liu2016wear_fig9a_m35nm", "torque ≠ (chave cega: varredura M0)"),
        ("liu2016wear_fig9a_m40nm", "torque ≠ (chave cega: varredura M0)"),
        ("liu2016wear_fig9a_m45nm", "torque ≠ (chave cega: varredura M0)"),
        ("liu2016wear_fig9a_m50nm", "torque ≠ (chave cega: varredura M0)"),
        ("liu2016wear_fig11a_af7p5kn", "A_F ≠ (chave cega: varredura de amplitude)"),
        ("liu2016wear_fig11a_af8p75kn", "A_F ≠ (chave cega: varredura de amplitude)"),
        ("liu2016wear_fig11a_af10kn", "A_F ≠ das irmãs; e suspeita de re-plot da fig7_run1"),
        ("liu2016wear_fig11a_af11p25kn", "A_F ≠ (chave cega: varredura de amplitude)"),
        ("liu2016wear_fig11a_af12p5kn", "A_F ≠ (chave cega: varredura de amplitude)"),
        ("liu2016wear_fig13a_dry", "lubrificação ≠ da MoS₂; e suspeita de re-plot da fig7_run1"),
        ("liu2016wear_fig13a_mos2", "lubrificação ≠ (MoS₂ × seco)"),
        ("liu2016wear_fig7_run1_1e6cyc", "só pareia com run2 (par declarado)"),
        ("liu2016wear_fig7_run2_5e6cyc", "só pareia com run1 (par declarado)"),
    )})
# 6ª ocorrência — **P-15, assinada pelo professor em 2026-08-08** (prereg
# `2026-08-08-p7-p15-execucao-prereg.md`; auditoria `pares_piso_auditoria.md`).
# A chave é cega à **carga AXIAL**, que é a variável varrida do ECCLES: ela
# juntava n=10 curvas de "sem axial" até 3,5 kN numa família só (δ=0,65 mm,
# F_amp=6000 N, disp). Os σ vão de 0,0195 (sem axial) a 0,1887 (4 kN) — quase
# **10×** e MONOTÔNICOS com a carga axial: não é dispersão de réplica, é o efeito
# que o paper estava medindo.
#
# ⚠️ DIFERENTE das 5 ocorrências acima, esta **NÃO é inócua**: o piso falso
# valia σ 0,0828, ou seja `limite_sres(ECCLES_2010)` = 0,0828 contra 0,0250 —
# **3,3× afrouxado** —, e exatamente **1** curva passava só por isso
# (`fig7c_axial_2p7kN`, σ 0,0258 = 3 % acima do limite global). Bloquear CUSTA
# −1 no censo, e foi assinado sabendo disso.
#
# ⚠️ INCONSISTÊNCIA INTERNA que isto resolve: as exceções F5 assinadas do próprio
# ECCLES argumentam **"sobreposição axial"** — a campanha tratava a carga axial
# como DISTINTIVA ao provar exceção e como IRRELEVANTE ao medir piso.
_SEM_FAMILIA_MECANICA.update({
    cid: "carga axial ≠ (chave cega: é a variável varrida do ECCLES)"
    for cid in (
        "eccles2010_fig3_typical_no_axial",
        "eccles2010_fig6_annotated_4kN_axial",
        "eccles2010_fig7a_no_axial",
        "eccles2010_fig7b_axial_1p1kN_constant",
        "eccles2010_fig7c_axial_2p7kN_constant",
        "eccles2010_fig7d_axial_3p1kN_constant",
        "eccles2010_fig8a_no_axial_baseline1",
        "eccles2010_fig8b_axial_0p7kN_intermittent",
        "eccles2010_fig8c_no_axial_baseline2",
        "eccles2010_fig8d_axial_3p5kN_intermittent",
    )})
# 6ª ocorrência da MESMA classe (2026-08-06, campanha MARGENS) — e a primeira
# que CUSTA uma curva. No SUN_2025_CRIMP **NÃO EXISTE par de réplica válido**:
# toda família que a chave cega forma cruza uma variável VARRIDA do artigo.
#   fam δ=0,3 F=6000  n=4 → pareia porca CRIMP × PADRÃO **e** COM × SEM graxa
#                            ⇒ piso MAE **0,448** · σ 0,14077 (isso não é
#                            dispersão de réplica, é o ASSUNTO do paper)
#   fam δ=0 F=7500    n=2 → crimp × padrão (axial 7,5 kN)   σ 0,03462
#   fam δ=0 F=17500   n=2 → crimp × padrão (axial 17,5 kN)  σ 0,02340
# Média por fonte ⇒ `limite_sres` = **0,06627 = 2,65× o global**.
# ⚠️ CUSTO MEDIDO E ACEITO: bloquear leva o limite a 0,0250 e a
# `transverse_grease_crimp` **SAI do tripé** (σ 0,0303 = 1,21×); a fonte vai de
# 7/8 para 6/8 e o censo de 139 para 138. É a 1ª vez que esta higiene custa
# curva — as 5 anteriores foram inócuas. Executada assim mesmo: um piso que
# mede a diferença entre os dois tratamentos comparados pelo artigo não é piso,
# e afrouxar barra com ele é o oposto do que a 3ª perna existe para fazer.
# Precedentes de aceitar perda de censo por correção: retratação CACCESE
# (2026-08-04) e a saída da `yang2021_r1` no D-U (2026-08-06).
_SEM_FAMILIA_MECANICA.update({
    cid: motivo for cid, motivo in (
        ("sun2025efa109235_transverse_grease_standard",
         "tipo de porca ≠ e lubrificação ≠ (chave cega) — são as variáveis "
         "varridas do artigo"),
        ("sun2025efa109235_transverse_grease_crimp",
         "tipo de porca ≠ e lubrificação ≠ (chave cega)"),
        ("sun2025efa109235_transverse_nogrease_standard",
         "tipo de porca ≠ e lubrificação ≠ (chave cega)"),
        ("sun2025efa109235_transverse_nogrease_crimp",
         "tipo de porca ≠ e lubrificação ≠ (chave cega)"),
        ("sun2025efa109235_axial_F7.5kN_standard",
         "tipo de porca ≠ (chave cega: crimp × padrão a 7,5 kN)"),
        ("sun2025efa109235_axial_F7.5kN_crimp",
         "tipo de porca ≠ (chave cega: crimp × padrão a 7,5 kN)"),
        ("sun2025efa109235_axial_F17.5kN_standard",
         "tipo de porca ≠ (chave cega: crimp × padrão a 17,5 kN)"),
        ("sun2025efa109235_axial_F17.5kN_crimp",
         "tipo de porca ≠ (chave cega: crimp × padrão a 17,5 kN)"),
    )})
# 7ª ocorrência (2026-08-06, D-X): no KARLSEN_2022 a chave cega pareava
# `run21p0` (M42 **HV**, cai a 0,073) com `run29p0` (M42 **Vibralock
# torqueado**, plano em 0,949) — só porque `F_amp = 0,4·F₀` e ambas têm
# F₀=685 kN. O **sistema de porca é a variável independente do paper**
# ("Comparative study on loosening of anti-loosening bolt and standard bolt
# system"), então esse par é contraste, não réplica: piso 0,3666/0,8336/**0,2639**.
# Bloqueadas as 4 vibralock ⇒ piso da fonte 0,2348/0,5402/0,1742 →
# **0,1031/0,2468/0,0845** e `limite_sres` 0,17418 → **0,08449**.
# Censo da fonte inalterado (10/11 antes e depois) — mas ver a retratação da
# `run14p2` abaixo: a correção **criou** a violação de σ nela.
# ⚠️ Declarar a família M30-HV inteira (4 espécimes) como réplica daria piso σ
# **0,1644** (6,6× o global) e cobriria tudo — **recusado**: salvar exceção
# afrouxando a barra é o inverso da regra. Se o professor julgar que os 4 são
# réplicas legítimas (F₀ alcançado varia 312–340 kN, 9 %), é decisão dele.
# BLOQUEIO 2026-08-10 (auditoria de ANCORA, `yang2021_ancora_replicas_resultado.md`
# + `piso_ancora_auditoria_resultado.md`): a chave mecanica pareia
# `yang2021_fig2_typical` com `yang2021_amp0p8mm_ax6kN` como replicas de delta=0,8 mm
# — mas a nota de aparato declara que **a condicao da Fig. 2 NAO e' rotulada no
# paper** ("0.8 mm is a plausible assumption by the life family") e que a Fig. 2 e'
# uma **medicao INDEPENDENTE** da Fig. 6(a3) (fins 5980 vs 5655, +0,17 kN de
# offset). Parear uma condicao ASSUMIDA como replica de uma medida e' a mesma classe
# de defeito que os blocos ROUSSEAU (espessuras) e KARLSEN (sistema de porca).
# ⚠️ INOCUO HOJE, e listado assim mesmo: o piso registrado do YANG_2021 e' None (o
# limite global 0,025 vence) e NENHUMA das duas usa prova de piso — as duas tem
# excecao **F5 §C** ("canal estrutural xi-dependente confundido"), com F7=None.
# Verificado antes de mexer, pela regra de LER A PROVA GRAVADA. O bloqueio impede
# que uma futura prova F7 se apoie neste par: o piso CRU dele e' 0,0308 e o
# re-ancorado na janela comum e' 0,0182 — **1,7x de inflacao por ANCORA** (as duas
# comecam em ciclos diferentes, 300 e 500).
_SEM_FAMILIA_MECANICA.update({
    cid: motivo for cid, motivo in (
        ("yang2021_fig2_typical",
         "condicao NAO ROTULADA no paper (delta assumido) — nao e' replica de "
         "medicao declarada; piso cru inflado 1,7x por ancora"),
        ("yang2021_amp0p8mm_ax6kN",
         "par com a fig2, cuja condicao e' ASSUMIDA (chave cega ao rotulo)"),
    )})

_SEM_FAMILIA_MECANICA.update({
    cid: motivo for cid, motivo in (
        ("karlsen2022_M30_vibralock_run9p0",
         "sistema de porca ≠ (chave cega: Vibralock × HV)"),
        ("karlsen2022_M30_vibralock_torqued_run16p0",
         "sistema de porca ≠ (chave cega: Vibralock × HV)"),
        ("karlsen2022_M42_vibralock_run23p0",
         "sistema de porca ≠ (chave cega: Vibralock × HV)"),
        ("karlsen2022_M42_vibralock_torqued_run29p0",
         "sistema de porca ≠ (chave cega: Vibralock torqueado × M42 HV — "
         "era o par que inflava o piso a σ 0,2639)"),
    )})

# RETRATADAS em 2026-08-01 (erratum ROUSSEAU, dupla causa): (a) o piso da
# fonte (0,546/0,206/0,186) vinha do par aço-t10↔aço-t12 — espessuras
# diferentes pareadas como réplicas pela chave cega à geometria (mesma classe
# do piso inválido do LU, retratado em 31/07); (b) o drive do aço estava 10×
# errado no registry (0,5 vs 0,05/0,05/0,04 mm da Tabela 2 do PDF oficial,
# baixado na Rodada 6). Prova preservada; re-assinatura exige piso VÁLIDO.
# Retiradas D1 (30/07) cuja base ERA o mesmo piso retratado no erratum: na
# época a retirada estava certa (passavam sob max(0,025; 0,186)); com o piso
# falso removido elas voltam a falhar POR MOTIVO NOVO — não se devolve a
# assinatura (seria re-assinar contra piso inválido); ficam na FILA. O guard
# `test_excecao_assinada_esta_de_fato_fora_do_tripe` lê esta lista.
_RETIRADAS_D1_INVALIDADAS_POR_ERRATUM = {
    "rousseau2025_hdpe_t14",
    "rousseau2025_steel_t12",
    # mesma lógica, 2026-08-01 (prereg familias-falsas-chave-cega): a
    # retirada D1 destas duas se apoiava no piso σ 0,2214 do JCSR, que era
    # dispersão entre 5 AMBIENTES tratados como réplicas pela chave cega.
    # Removido o piso falso, elas voltam a falhar — por motivo NOVO, então
    # a assinatura não é devolvida (seria re-assinar contra piso inválido).
    "jcsr2023_galv_seawater",
    "jcsr2023_plain_seawater",
    # 3ª ocorrência da MESMA estrutura, 2026-08-06 (bloqueio da 6ª chave cega,
    # `sun_crimp_resultado.md`): a retirada D1 desta curva se apoiava no piso
    # σ 0,066 do SUN — e a própria prova preservada em `_EXCECOES_RETIRADAS_D1`
    # a denuncia, porque ela diz textualmente "σ 0.030/0.066". Aquele 0,066 é
    # dispersão entre porca CRIMP × PADRÃO e COM × SEM graxa (as duas variáveis
    # que o artigo compara; a família δ=0,3 tem piso MAE 0,448). Removido o
    # piso falso, a curva volta a falhar (σ 0,0303 = 1,21× o limite global) —
    # por motivo NOVO, então a assinatura NÃO é devolvida: seria re-assinar
    # contra piso inválido. Custo já declarado na execução: resolvida −1.
    # Detectada pelo invariante `test_excecao_assinada_esta_de_fato_fora_do_
    # tripe`, não a olho — eu havia escrito o custo em prosa e esquecido a
    # contabilidade em código.
    "sun2025efa109235_transverse_grease_crimp",
    # 4ª ocorrência da MESMA estrutura, 2026-08-08 (**P-15 assinada e
    # executada**; prereg `2026-08-08-p7-p15-execucao-prereg.md`). A retirada D1
    # desta curva se apoiava no piso σ **0,083** do ECCLES — e, como no SUN, a
    # própria prova preservada em `_EXCECOES_RETIRADAS_D1` a denuncia: ela diz
    # textualmente **"prova de piso (FORTE): σ 0.026/0.083"**. Aquele 0,083 era
    # dispersão entre cargas AXIAIS de 0 a 3,5 kN — a variável varrida do paper
    # —, com σ indo de 0,0195 a 0,1887 e MONOTÔNICO com a carga.
    # Removido o piso falso, a curva volta a falhar (σ 0,0258 = 1,03× o limite
    # global) — por motivo NOVO, então a assinatura NÃO é devolvida: seria
    # re-assinar contra piso inválido. Custo previsto e aceito na assinatura:
    # censo 140 → 139.
    # ⚠️ Consequência: a `fig7c` fica **sem estatuto E sem rota** — a fonte
    # perdeu o piso junto com a família falsa, logo prova F7 é impossível para
    # ela até haver réplica de condição repetida.
    "eccles2010_fig7c_axial_2p7kN_constant",
    # 4ª e 5ª ocorrências da MESMA estrutura, 2026-08-14 (execução de G+H,
    # commit `2335090`, a partir de `New_Theory/icmez_chave_cega_ao_grip.md`):
    #
    #  · ICMEZ_2025 — a retirada D1 destas 5 se apoiava no piso σ 0,0574, que
    #    vinha de 4 famílias pareando `grip_mm` 13,8 × 19,8 mm (COMPRIMENTO DE
    #    APERTO — rigidez de junta, a variável do desenho 2×2×2 do paper). Os
    #    MAEs de piso 0,105–0,209 nunca foram repetibilidade;
    #  · CHU_2026 — a `test5` se apoiava no piso σ 0,0507, que é a MÉDIA de
    #    duas famílias: uma legítima (`test5` × `test6_repeat`, σ 0,0296) e uma
    #    cega à RUGOSIDADE (`Ra1p6um_test9` × `test3`, σ 0,0718, iguais só
    #    porque o config usa o `RZ_DEFAULT` nas duas). Removida a falsa, o
    #    limite cai a 0,0296 e a `test5` (σ 0,0436) volta a falhar — e ela vem
    #    da família BOA: era a ruim que a mascarava.
    #
    # Em ambos, motivo NOVO ⇒ a assinatura NÃO é devolvida (seria re-assinar
    # contra piso inválido); ficam na FILA. Custo medido e pago: censo 146→140,
    # com predição 10/10 exata (as 6 que sairiam saíram; as 4 que sobreviveriam
    # por mérito sobreviveram).
    # ⚠️ As 5 do ICMEZ ficam SEM ROTA F7 — a fonte perdeu a família junto com o
    # piso falso, e o desenho do paper não tem condição repetida. A `test5` do
    # CHU TEM rota: sua família legítima existe e é declarada.
    "demir2024_amp0p3_F14p3_lk13p8",
    "demir2024_amp0p3_F14p3_lk19p8",
    "demir2024_amp0p3_F17p6_lk13p8",
    "demir2024_amp0p3_F17p6_lk19p8",
    "demir2024_amp0p4_F17p6_lk13p8",
    "chu2026ti_D1p0mm_F0_49kN_test5",
}

_EXCECOES_RETRATADAS_ROUSSEAU_PISO_INVALIDO = {
    "rousseau2025_hdpe_t10": (
        "prova de piso (FORTE): res.máx 0.153/0.546 · MAE 0.058/0.206 · σ 0.057/0.186"),
    "rousseau2025_hdpe_t12": (
        "prova de piso (FORTE): res.máx 0.138/0.546 · MAE 0.064/0.206 · σ 0.056/0.186"),
    "rousseau2025_steel_t10": (
        "prova de piso (FORTE): res.máx 0.188/0.546 · MAE 0.087/0.206 · σ 0.098/0.186"),
}


def _pisos_medidos(pares) -> dict:
    """PISO DE REPETIBILIDADE do próprio dado, recomputado na geração.

    `pares` = [(source, CaseResult)]. Uma família é o conjunto de curvas da
    MESMA fonte na MESMA condição nominal — lida do `config_used`
    (`delta_mm`, `F_amp_N`, `mode`), **não** do nome do arquivo, para não
    depender de convenção de sufixo (`_rep1`, `_t3`, `_test2`, `run1p2`…).
    Para cada PAR da família compara DADO contra DADO e mede as três réguas do
    tripé; o piso é a média dos pares.

    A comparação é feita por INTERPOLAÇÃO das duas curvas de dado numa grade de
    40 pontos na janela de x **comum** (interseção). A 1ª versão exigia
    abscissas idênticas (x arredondado) e isso **enviesava o piso para baixo por
    amostragem**: no BAUER fig6 sobrava 1 par dos 15, e não um par qualquer — o
    que por acaso caiu na mesma grade, que era o mais próximo. Medido: piso de
    MAE 0,0218 com 1 par contra **0,0959** com os 15, e o `FLOORS` legado do repo
    (pareado por nome) dizia 0,115 ⇒ era a 1ª versão que estava fora de linha,
    não o legado. Interpola-se o **dado**, nunca a métrica — a métrica continua
    lendo os vetores que o runner gravou (defeito de 2026-07-27).

    Por que isto vive no report e não numa constante: o limite é uma DECISÃO
    (constante), mas o piso é uma MEDIÇÃO — se o store mudar, o piso muda, e a
    página tem de dizer o número novo em vez de repetir o velho. É o que impede
    a justificativa dos limites de envelhecer em silêncio (regra §4.43).

    Devolve `{"fam": [(rótulo, n, MAE, max, σ)], "med": (MAE, max, σ),
              "por_fonte": {src: (MAE, max, σ)}}` com as medianas em `med`.
    """
    grupos: Dict[tuple, list] = {}
    grupos_cids: Dict[tuple, list] = {}
    por_cid = {}
    _vc = {r.case_id: r.validation_case for r in all_records()}
    for src, res in pares:
        x = getattr(res, "metric_x", None)
        d = getattr(res, "metric_data", None)
        if not (x and d and len(x) == len(d) >= 4):
            continue
        cid = getattr(res, "case_id", None)
        if cid:
            por_cid[cid] = (src, x, d)
        # BLOQUEIO de pareamento FALSO (2026-08-01, erratum ROUSSEAU): a
        # chave mecânica abaixo era CEGA à geometria per-case — os aços
        # t10/t12 (ESPESSURAS diferentes, a variável varrida do paper)
        # casavam como "réplicas" e o piso resultante assinou 3 exceções
        # FORTE inválidas. Curvas em _SEM_FAMILIA_MECANICA nunca entram em
        # família automática (pares declarados continuam possíveis).
        # ⚠️ SUPERSEDIDO POR MECANISMO em 2026-08-23 nas fontes de
        # `_FONTES_RESOLVIDAS_POR_CHAVE`: a chave passou a LER a variável
        # varrida, então bloquear ali seria proibir o pareamento CORRETO
        # (era o caso do par legítimo `eccles fig8a`×`fig8c`, que a lista
        # proibia). Os motivos ficam escritos — são procedência, não lixo.
        if cid in _SEM_FAMILIA_MECANICA and src not in _FONTES_RESOLVIDAS_POR_CHAVE:
            continue
        cfg = getattr(res, "config_used", None) or {}
        try:
            k = (src, round(float(cfg.get("delta_mm") or 0), 4),
                 round(float(cfg.get("F_amp_N") or 0), 1), cfg.get("mode"))
        except (TypeError, ValueError):
            continue
        # CHAVE ESTENDIDA (prereg `2026-08-23-chave-estendida-pareamento`): os
        # campos que o paper VARRE entram na identidade da condição. Sem eles a
        # chave dizia "mesma condição" para curvas que diferem em carga axial,
        # grip, rugosidade, espessura, remontagem ou espécime — e foi disso que
        # saíram 7 retratações de exceção. `None` (curva fora do registry) cai
        # numa tupla vazia e mantém o comportamento antigo.
        vc = _vc.get(cid) if cid else None
        if vc is not None:
            k = k + tuple(getattr(vc, campo, None) for campo in _CAMPOS_VARRIDOS)
        grupos.setdefault(k, []).append((x, d))
        grupos_cids.setdefault(k, []).append(cid)   # p/ o dedup dos declarados
    # PARES DECLARADOS (prereg 2026-07-31-pares-replica-declarados): réplicas
    # cujo F0 ALCANÇADO difere (aperto nunca repete: 4-14% nos pares do LU) e
    # que a chave mecânica nunca casaria. Lista explícita com proveniência —
    # mesmo padrão de _EXCECOES/_DECLARADAS; a chave mecânica continua para
    # as famílias automáticas e as demais fontes ficam bit-idênticas (G4).
    # ⚠️ DEDUP (2026-08-23, prereg `fecha-tickets-e-dedup`): se a chave
    # automatica JA agrupa os dois membros, a entrada declarada e' REDUNDANTE e
    # contaria o MESMO par duas vezes — inflando o piso da fonte e enviesando as
    # medianas globais. Antes da chave estendida isso nao acontecia (as curvas
    # estavam bloqueadas a mao); depois dela, 3 de 5 pares ficaram duplicados, e
    # com o fecho dos 3 tickets seriam 4 de 5. Este e' o proposito declarado do
    # mecanismo: alcancar pares que a chave "NUNCA casaria".
    # Custo medido do conserto: as 2 provas de piso do ECCLES perdem o
    # denominador e foram RETRATADAS — elas repousavam no par declarado, que os
    # 6 pares da familia mostram ser o MAIS FROUXO dos seis (mx 0.1866 e sigma
    # 0.0707, os dois maximos), pesado em dobro.
    _familias = [set(v) for v in grupos_cids.values() if len(v) > 1]
    for cid_a, cid_b, rotulo in _PARES_REPLICA_DECLARADOS:
        a, b = por_cid.get(cid_a), por_cid.get(cid_b)
        if not (a and b and a[0] == b[0]):
            continue
        if any(cid_a in fam and cid_b in fam for fam in _familias):
            continue                      # a chave ja faz este par
        grupos[(a[0], "DECL", rotulo, None)] = [(a[1], a[2]),
                                                (b[1], b[2])]
        grupos_cids[(a[0], "DECL", rotulo, None)] = [cid_a, cid_b]
    fam, por_fonte, membros = [], {}, {}
    for k, cs in grupos.items():
        if len(cs) < 2:
            continue
        ps = []
        for i in range(len(cs)):
            for j in range(i + 1, len(cs)):
                xi, yi = np.asarray(cs[i][0], float), np.asarray(cs[i][1], float)
                xj, yj = np.asarray(cs[j][0], float), np.asarray(cs[j][1], float)
                lo = max(xi.min(), xj.min())
                hi = min(xi.max(), xj.max())
                if hi <= lo:      # janelas de x disjuntas ⇒ não são réplicas
                    continue
                g = np.linspace(lo, hi, 40)
                dif = np.interp(g, xi, yi) - np.interp(g, xj, yj)
                ps.append((float(np.mean(np.abs(dif))),
                           float(np.max(np.abs(dif))), float(np.std(dif))))
        if ps:
            trio = tuple(sum(p[i] for p in ps) / len(ps) for i in range(3))
            rot = (f"{k[0]} [par declarado: {k[2]}]" if k[1] == "DECL"
                   else f"{k[0]} δ={k[1]:g} F={k[2]:.0f}")
            fam.append((rot, len(cs)) + trio)
            por_fonte.setdefault(k[0], []).append(trio)
            membros[rot] = [c for c in grupos_cids.get(k, []) if c]
    med = tuple(float(np.median([f[2 + i] for f in fam])) if fam else 0.0
                for i in range(3))
    return {"fam": sorted(fam, key=lambda z: -z[2]), "med": med,
            # "membros": rótulo -> case_ids da família (aditivo, 2026-08-31;
            # o §4.5 do artigo compara o erro do modelo com o piso POR FAMÍLIA
            # e precisa saber quem é membro de quem — mesma fonte única).
            "membros": membros,
            "por_fonte": {s: tuple(sum(t[i] for t in v) / len(v)
                                   for i in range(3))
                          for s, v in por_fonte.items()}}


def _svg_hist(vals, xlabel: str, w: int = 272, h: int = 158,
              step: float = 0.05, nb: int = 10,
              meta: Optional[float] = META,
              warn_from: Optional[float] = None,
              key: str = "", ref: Optional[tuple] = None) -> str:
    """Histograma com a META marcada. Barras abaixo da meta em verde, acima
    em vermelho — a leitura "quanto falta" fica imediata. Último bin é
    transbordo (>= step*nb).

    `meta=None` desliga a linha tracejada (para eixos que não são erro em
    F/F₀ — ex. a fração adimensional de erro sistemático, que não tem meta
    declarada; inventar uma linha ali seria fabricar um gate).
    `warn_from` colore a partir de outro valor que não a meta: serve para
    marcar uma FAIXA de leitura (não um limite aprovado).
    `ref=(valor, rótulo)` desenha uma linha de REFERÊNCIA discreta — usada para
    o piso de repetibilidade medido no eixo do σ_res: sem ela o leitor não vê
    que o limite está perto do que o próprio experimento consegue repetir.
    `key` marca o SVG (`data-hist`) e publica a geometria em `data-*` para os
    controles ao vivo recolorirem as barras sem redesenhar nada."""
    if not vals:
        return ""
    ML, MR, MT, MB = 30, 8, 10, 30
    bins = [0] * (nb + 1)
    for v in vals:
        bins[min(int(max(v, 0.0) / step), nb)] += 1
    ymax = max(bins) or 1
    pw = (w - ML - MR) / (nb + 1)
    X = lambda k: ML + k * pw
    Y = lambda c: MT + (1 - c / ymax) * (h - MT - MB)
    lim = warn_from if warn_from is not None else meta
    out = []
    for k, c in enumerate(bins):
        lo, hi = k * step, (k + 1) * step
        acima = lim is not None and lo >= lim
        # A faixa CORTADA pelo limite não é verde nem vermelha: parte dela passa
        # e parte não. Pintá-la de verde faria o leitor contar aprovadas que não
        # existem (medido: com limite 0.025 e passo 0.01, o olho somava 124 onde
        # o número real era 109). Meia-opacidade + aviso no tooltip.
        meia = lim is not None and lo < lim < hi
        rot = (f"&ge; {lo:.4g}" if k == nb else f"{lo:.4g}–{hi:.4g}")
        y = Y(c)
        out.append(
            f'<rect data-lo="{lo:.6g}" data-hi="{hi:.6g}" '
            f'x="{X(k) + 1:.1f}" y="{y:.1f}" '
            f'width="{pw - 2:.1f}" '
            f'height="{max(h - MB - y, 0):.1f}" rx="2" style="fill:var('
            f'--{"good" if (not acima and not meia) else "warn"});'
            f'fill-opacity:{".45" if meia else ".8"}"><title>'
            f'{rot}: {c} curvas'
            f'{" — faixa CORTADA pelo limite: parte passa, parte não" if meia else ""}'
            f'</title></rect>')
        if c:
            out.append(f'<text x="{X(k) + pw / 2:.1f}" y="{y - 3:.1f}" '
                       f'text-anchor="middle" class="tk">{c}</text>')
    # linha de REFERÊNCIA (piso medido) — antes da meta, para ficar por baixo.
    # SEM rótulo desenhado, de propósito: quando o limite É o piso (o caso do
    # σ_res, por construção) os dois x coincidem e qualquer texto ali cai por
    # cima das barras — duas posições foram tentadas e as duas colidiram, visto
    # em captura de tela. A legenda vive no bloco `_explica` logo abaixo (onde
    # vive TODA legenda desta página) e o valor está no `<title>` da linha.
    if ref is not None and ref[0] is not None and 0 < ref[0] < step * (nb + 1):
        xr = X(ref[0] / step)
        out.append(f'<line data-ref="1" x1="{xr:.1f}" y1="{MT}" x2="{xr:.1f}" '
                   f'y2="{h - MB}" style="stroke:var(--mut);stroke-width:1.4" '
                   f'stroke-dasharray="2 3"><title>'
                   f'{_esc.escape(str(ref[1]))}</title></line>')
    # marca da meta + eixos
    if meta is not None:
        xm = X(meta / step)
        out.append(f'<line data-lim="1" x1="{xm:.1f}" y1="{MT}" x2="{xm:.1f}" '
                   f'y2="{h - MB}" class="rl" stroke-dasharray="4 3"/>'
                   f'<text data-limtxt="1" x="{xm + 4:.1f}" y="{MT + 9}" '
                   f'class="tk" style="fill:var(--err)">'
                   f'limite {meta:.4g}</text>')
    elif warn_from is not None:
        xw = X(warn_from / step)
        out.append(f'<line x1="{xw:.1f}" y1="{MT}" x2="{xw:.1f}" y2="{h - MB}" '
                   f'class="gl" stroke-dasharray="3 3"/>'
                   f'<text x="{xw - 4:.1f}" y="{MT + 9}" text-anchor="end" '
                   f'class="tk" style="fill:var(--warn)">'
                   f'&ge; {warn_from:.1f} unilateral</text>')
    out.append(f'<line x1="{ML}" y1="{h - MB}" x2="{w - MR}" y2="{h - MB}" '
               f'class="gl"/>')
    for k in (0, nb // 2, nb):
        out.append(f'<text x="{X(k):.1f}" y="{h - MB + 12}" '
                   f'text-anchor="middle" class="tk">{k * step:.4g}</text>')
    out.append(f'<text x="{(ML + w - MR) / 2:.0f}" y="{h - 3}" '
               f'text-anchor="middle" class="axl">{_esc.escape(xlabel)}</text>')
    return (f'<svg viewBox="0 0 {w} {h}" class="plot" role="img" '
            f'data-hist="{_esc.escape(key)}" data-step="{step:.6g}" '
            f'data-ml="{ML}" data-pw="{pw:.4f}" data-mt="{MT}" '
            f'data-hb="{h - MB}" '
            f'aria-label="{_esc.escape(xlabel)}">{"".join(out)}</svg>')


def _svg_scatter(pts, w: int = 560, h: int = 330) -> str:
    """MAE x res.máx, uma curva por ponto, com os quadrantes da meta. Responde
    de relance QUAL das duas métricas é o gargalo. `pts` = [(mae, maxerr)].

    SEM CHAMADOR desde 2026-07-29: o painel passou a usar `_svg_scatter3`, que
    contém este gráfico como a **sombra** no plano RMSE=0. Fica no arquivo de
    propósito — é o desenho 2D de referência, útil se alguém precisar do plano
    sem a profundidade (impressão em preto-e-branco, por exemplo). Se for
    remover, remova junto a menção à sombra no docstring do 3D."""
    if not pts:
        return ""
    ML, MR, MT, MB = 46, 14, 14, 40
    cap = 0.60                       # teto dos eixos; fora dele vira contagem
    X = lambda v: ML + min(v, cap) / cap * (w - ML - MR)
    Y = lambda v: MT + (1 - min(v, cap) / cap) * (h - MT - MB)
    out = []
    for g in range(5):                       # grade
        t = cap * g / 4
        out.append(f'<line x1="{ML}" y1="{Y(t):.1f}" x2="{w - MR}" '
                   f'y2="{Y(t):.1f}" class="gl"/>'
                   f'<text x="{ML - 6}" y="{Y(t) + 3:.1f}" text-anchor="end" '
                   f'class="tk">{t:.2f}</text>'
                   f'<text x="{X(t):.1f}" y="{h - MB + 14}" '
                   f'text-anchor="middle" class="tk">{t:.2f}</text>')
    # faixa do tripé (quadrante bom)
    out.append(f'<rect x="{ML}" y="{Y(META):.1f}" width="{X(META) - ML:.1f}" '
               f'height="{h - MB - Y(META):.1f}" style="fill:var(--good);'
               f'fill-opacity:.10"/>')
    out.append(f'<line x1="{X(META):.1f}" y1="{MT}" x2="{X(META):.1f}" '
               f'y2="{h - MB}" class="rl" stroke-dasharray="4 3"/>'
               f'<line x1="{ML}" y1="{Y(META):.1f}" x2="{w - MR}" '
               f'y2="{Y(META):.1f}" class="rl" stroke-dasharray="4 3"/>')
    fora_teto = 0
    for a, b in pts:
        if a > cap or b > cap:
            fora_teto += 1
        bom = a <= META and b <= META
        out.append(f'<circle cx="{X(a):.1f}" cy="{Y(b):.1f}" r="3" '
                   f'style="fill:var(--{"good" if bom else "warn"});'
                   f'fill-opacity:.65"><title>MAE {a:.3f} · res.máx {b:.3f}'
                   f'</title></circle>')
    out.append(f'<text x="{(ML + w - MR) / 2:.0f}" y="{h - 4}" '
               f'text-anchor="middle" class="axl">MAE</text>'
               f'<text x="13" y="{(MT + h - MB) / 2:.0f}" text-anchor="middle" '
               f'class="axl" transform="rotate(-90 13 '
               f'{(MT + h - MB) / 2:.0f})">resíduo máximo</text>')
    if fora_teto:
        out.append(f'<text x="{w - MR - 4}" y="{MT + 10}" text-anchor="end" '
                   f'class="tk" style="fill:var(--mut)">{fora_teto} curva(s) '
                   f'além de {cap:.2f} (recortadas na borda)</text>')
    return (f'<svg viewBox="0 0 {w} {h}" class="plot" role="img" '
            f'aria-label="dispersão MAE por resíduo máximo">'
            f'{"".join(out)}</svg>')


# Encurtamento default do eixo de profundidade (axonométrica). NÃO é escolha
# estética: é o ótimo MEDIDO em 2026-07-29 sobre as 202 curvas do store.
# O critério é a MENOR separação angular entre a direção da profundidade e as
# três direções com que ela pode ser confundida — o eixo x (0°), o eixo y (−90°)
# e o EIXO PRINCIPAL DA PRÓPRIA NUVEM (que aqui é ~−38°, porque MAE e res.máx
# são fortemente correlacionados pelo sanduíche `MAE <= RMSE <= res.máx`).
# O par antigo (0.30, 0.19) punha a profundidade a −25.3°, isto é a **12.5° da
# nuvem**: um ponto fundo era visualmente idêntico a um ponto com MAE e pico
# maiores, e a 3ª perna ficava ilegível POR CONSTRUÇÃO. Varredura em grade
# (dx 0.06–0.62 × dy 0.04–0.46) → máximo da menor separação em (0.08, 0.30):
# profundidade a −64.8°, separação 25.2° (2.0× melhor), equidistante da nuvem e
# do eixo y. Refazer a medição se a nuvem mudar de forma (o script está no
# changelog de 2026-07-29).
_ROT3 = (0.08, 0.30)

# Cor de cada perna, usada como CÓDIGO no 3D: o ponto assume a cor da perna que
# ele estoura pelo MAIOR múltiplo do limite — "a perna que manda". São as cores
# dos próprios eixos, para o código se auto-documentar (MAE = azul `--di`,
# res.máx = laranja `--warn`, 3ª perna = ouro `--accent`, que já era a cor do
# eixo de profundidade). Verde `--good` = passa nas três.
# Antes de 2026-07-29 (tarde) TODA reprovação era laranja: o gráfico cuja
# manchete é *"qual perna é o gargalo"* respondia a pergunta só no texto abaixo.
_COR_PERNA = {"mae": "di", "mx": "warn", "sd": "accent", None: "good"}

# Rampa CONTÍNUA verde→âmbar→vermelho da distância à origem (pedido do professor
# 2026-07-29: *"pode ter um gradiente do vermelho ao verde do quão próximo está
# do eixo (0,0,0)"*). A origem é o modelo perfeito (erro zero nas três pernas).
#
# A distância é medida em **múltiplos do limite** e na norma do MÁXIMO —
# `d = max(MAE/lim, res.máx/lim, σ_res/lim)` —, não em euclidiana. O motivo é
# que assim a cor e a caixa NUNCA se contradizem: `d <= 1` é *exatamente* o
# veredito do tripé (que é uma conjunção, isto é uma condição L∞), então o
# âmbar cai na superfície da caixa por construção. Na euclidiana isso falha:
# (1.5, 0.1, 0.1)× tem norma 0.87 e ainda assim reprova no MAE, e a cor diria
# "verde" sobre um ponto fora da caixa.
# E as duas leituras de cor passam a ser o mesmo número partido em dois: o
# GRADIENTE é o max ("quão longe"), a PERNA QUE MANDA é o argmax ("por onde").
#
# Hexes FIXOS, não vars de tema, e de propósito: interpolar exige número, e o
# valor de `--good` muda entre claro e escuro. Estes três são de meio-tom, legíveis
# nos dois fundos (#faf9f7 e #16140f). As cores DISCRETAS (perna que manda)
# seguem sendo vars de tema — codificações diferentes, sistemas diferentes.
_RAMPA = ((0x1f, 0x9d, 0x55), (0xe0, 0xa4, 0x11), (0xd1, 0x3b, 0x2e))
_RAMPA_TETO = 3.0        # d >= 3x o limite satura no vermelho


def _cor_rampa(d: float) -> str:
    """Cor da rampa para uma distância `d` em múltiplos do limite: verde em 0,
    âmbar exatamente em 1 (a superfície da caixa de aceitação) e vermelho
    saturado em `_RAMPA_TETO`. Interpolação linear em RGB, em dois trechos."""
    a, b = (_RAMPA[0], _RAMPA[1]) if d <= 1.0 else (_RAMPA[1], _RAMPA[2])
    t = (min(max(d, 0.0), 1.0) if d <= 1.0
         else min((d - 1.0) / (_RAMPA_TETO - 1.0), 1.0))
    return "#%02x%02x%02x" % tuple(
        int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def _severidade(a, b, c, lx, ly, lz) -> float:
    """`d` da rampa: o MAIOR múltiplo de limite estourado pela curva. `<= 1`
    ⟺ passa no tripé. Sem σ_res a curva não é julgável na 3ª perna ⇒ `inf`
    (nunca verde), mesma regra de `_tripe_ok` e de `_perna_manda`."""
    if c is None:
        return float("inf")
    return max(a / lx, b / ly, c / lz)


def _perna_manda(a, b, c, lx, ly, lz):
    """Qual das três pernas reprova a curva pelo MAIOR múltiplo do seu limite;
    `None` = passa nas três.

    Comparar MÚLTIPLOS, e não valores brutos, é o que torna as pernas
    comensuráveis: res.máx 0.12 contra limite 0.10 é violação de 1.2×, enquanto
    MAE 0.12 contra 0.05 é 2.4× — o segundo é o gargalo, embora o número seja o
    mesmo. É a mesma normalização do modo "×limite" do gráfico.

    `c is None` (sem σ_res) **nunca** vira verde: sem a medição a curva não é
    julgável na 3ª perna, e aprová-la seria ignorar a perna (mesma regra de
    `_tripe_ok`)."""
    if c is None:
        return "sd"
    fora = [t for t in ((a / lx, "mae"), (b / ly, "mx"), (c / lz, "sd"))
            if t[0] > 1.0]
    return max(fora)[1] if fora else None


def _mult_grade(cap: float, lim: float, nmax: int = 8):
    """Posições das linhas de grade de um eixo: **múltiplos inteiros do limite**
    daquela perna, em vez de quartos do teto.

    A 1ª linha é o próprio limite, e por construção ela COINCIDE com a aresta da
    caixa de aceitação — logo a distância entre linhas *é* uma unidade de
    limite, e se lê "este ponto está entre a 3ª e a 4ª linha ⇒ 3–4× o limite"
    contando, sem conta mental. Antes, com quartos do teto, o teto de x era 0.30
    e o limite 0.05: nenhuma linha caía no limite e não havia como ler a aresta
    da caixa contra a escala.

    Cai em quartos quando não há limite declarado (RMSE, |viés|) ou quando o
    teto passa de `nmax` limites (a grade ficaria densa demais)."""
    if lim and lim > 0 and cap / lim <= nmax + 0.51:
        k = max(1, int(round(cap / lim)))
        return [(i + 1) * cap / k for i in range(k)]
    return [cap * (i + 1) / 4 for i in range(4)]


# Razao maxima de DURACAO para uma familia poder ser colapsada em condicao.
# Medido em 2026-08-23 (`estudo_das_replicas.md`): comparar curvas de duracoes
# muito diferentes no CICLO ABSOLUTO inflou a banda de 4 condicoes em 55-65%,
# porque a curva curta ja terminou quando a longa esta no meio da vida. E acima
# de ~3x a propria normalizacao por vida perde sentido: "50% da vida" entre um
# ensaio de 1.041 e outro de 693.750 ciclos nao e um estado fisico comum.
# ⚠️ NAO se resolve pondo duracao na chave de familia: duracao e' ALCANCADA
# quando o ensaio corre ate um critério (o BAUER para quando a pre-carga cai) e
# AJUSTADA quando corre ciclos fixos — e grandeza alcancada na chave destroi
# pareamento legitimo, como a falsificacao de `initial_preload_N` mostrou.
_RAZAO_DUR_MAX = 3.0


def _graficos_replica_html(comp, results, pisos) -> str:
    """Tres graficos que os estudos de 2026-08-23/25 produziram e a pagina nao
    mostrava: artefato de duracao, custo x qualidade do dado, e procedencia.

    Todos RECOMPUTADOS na geracao — nenhum numero fixo em prosa (regra §4.43).
    """
    import collections
    import itertools
    import numpy as np
    from . import runner as _rn

    vcs = {r.case_id: r.validation_case for r in comp}
    recs = {r.case_id: r for r in comp}

    # --- familias pela MESMA chave de `_pisos_medidos` --------------------
    gr = collections.defaultdict(list)
    for r in comp:
        res = results.get(r.case_id)
        if res is None or not getattr(res, "metric_x", None):
            continue
        if (r.case_id in _SEM_FAMILIA_MECANICA
                and r.source not in _FONTES_RESOLVIDAS_POR_CHAVE):
            continue
        cfg = getattr(res, "config_used", None) or {}
        try:
            k = (r.source, round(float(cfg.get("delta_mm") or 0), 4),
                 round(float(cfg.get("F_amp_N") or 0), 1), cfg.get("mode"))
        except (TypeError, ValueError):
            continue
        vc = vcs.get(r.case_id)
        if vc is not None:
            k = k + tuple(getattr(vc, campo, None) for campo in _CAMPOS_VARRIDOS)
        gr[k].append(r.case_id)

    # --- G1: banda em ciclo x banda em VIDA NORMALIZADA -------------------
    linhas = []
    for k, cids in gr.items():
        if len(cids) < 2:
            continue
        # ⚠️ Os MESMOS vetores que `_pisos_medidos` usa — `metric_x`/`metric_data`,
        # nao a CSV crua. O grafico afirma "quanto da banda PUBLICADA e'
        # artefato", e a banda publicada sai desses vetores; medir na CSV crua
        # explicaria uma banda que a pagina nao publica. Foi assim que a 1a
        # versao barrou `LIU_2016` (5x cru) e deixou passar o `ECCLES` (7x na
        # janela), contradizendo o censo logo acima na mesma pagina.
        C = {}
        for c in cids:
            res_c = results.get(c)
            x = getattr(res_c, "metric_x", None)
            y = getattr(res_c, "metric_data", None)
            if not (x and y and len(x) == len(y) >= 5):
                continue
            x = np.asarray(x, float)
            y = np.asarray(y, float)
            if x.max() > 0:
                C[c] = (x, y)
        if len(C) < 2:
            continue
        dur = [x.max() for x, _y in C.values()]
        razao = max(dur) / max(min(dur), 1e-9)
        lo = max(x.min() for x, _y in C.values())
        hi = min(dur)
        if hi <= lo:
            continue
        g = np.linspace(lo, hi, 40)
        Z = {c: np.interp(g, *C[c]) for c in C}
        b_abs = max(np.abs(Z[a] - Z[b]).max()
                    for a, b in itertools.combinations(C, 2))
        u = np.linspace(0.05, 1.0, 40)
        Y_ = {c: np.interp(u * C[c][0].max(), *C[c]) for c in C}
        b_nrm = max(np.abs(Y_[a] - Y_[b]).max()
                    for a, b in itertools.combinations(C, 2))
        linhas.append((k[0], len(C), float(razao), float(b_abs), float(b_nrm)))

    # ⚠️ Acima de ~3x a normalizacao por vida perde sentido: "50% da vida" entre
    # um ensaio de 1.041 e outro de 693.750 ciclos nao e' um estado fisico
    # comum. Essas familias entram na LISTA de fora, nao no grafico.
    ok_dur = [l for l in linhas if l[2] <= _RAZAO_DUR_MAX]
    fora_dur = [l for l in linhas if l[2] > _RAZAO_DUR_MAX]
    rows1 = [(f"{f} ({n})", min(bn, ba), ba,
              f"{100 * (1 - min(bn, ba) / ba):.0f}% artefato")
             for f, n, _rz, ba, bn in sorted(ok_dur, key=lambda q: -q[3])]
    pior = (max(((1 - min(bn, ba) / ba), f) for f, _n, _r, ba, bn in ok_dur)
            if ok_dur else (0.0, ""))

    # --- G2: custo (constantes) x qualidade do dado (banda) ---------------
    k_por_fonte = collections.Counter()
    vistos = set()
    for r in comp:
        g_ = _rn._adopted_for(r.source, r.case_id,
                              getattr(vcs[r.case_id], "bolt_size", "") or "")
        if not g_ or g_ in vistos:
            continue
        vistos.add(g_)
        c = (kb.adopted_config(g_) or {}).get("cfg") or {}
        n = sum(1 for kk, vv in c.items()
                if kk != "per_case" and isinstance(vv, (int, float))
                and not isinstance(vv, bool))
        n += sum(len(d) for d in (c.get("per_case") or {}).values()
                 if isinstance(d, dict))
        k_por_fonte[r.source] += n
    banda_fonte = {}
    for f, _n, _rz, ba, _bn in linhas:
        banda_fonte[f] = max(banda_fonte.get(f, 0.0), ba)
    pts2 = [(banda_fonte[f], k_por_fonte[f],
             f.replace("_20", "").replace("_", " ")[:13])
            for f in sorted(banda_fonte) if k_por_fonte.get(f)]

    # --- G3: procedencia das entradas per_case ---------------------------
    com_prov = collections.Counter()
    sem_prov = collections.Counter()
    for s in kb.adopted_sources():
        e = kb.adopted_config(s) or {}
        c = e.get("cfg") or {}
        prov = e.get("prov") or {}
        for _tok, d in (c.get("per_case") or {}).items():
            if not isinstance(d, dict):
                continue
            for campo in d:
                alvo = com_prov if campo in prov else sem_prov
                alvo[s.split("_20")[0]] += 1
    fontes3 = sorted(set(com_prov) | set(sem_prov),
                     key=lambda f: -(com_prov[f] + sem_prov[f]))[:9]
    rows3 = [(f, com_prov[f], com_prov[f] + sem_prov[f],
              f"{com_prov[f]}/{com_prov[f] + sem_prov[f]}") for f in fontes3]
    tot3 = sum(com_prov.values()) + sum(sem_prov.values())

    n_perde = sum(1 for _f, _n, _r, ba, bn in ok_dur if bn < 0.7 * ba)
    g1 = (f'<h3>Quanto da "banda" é artefato de DURAÇÃO</h3>'
          f'<div class="explica">'
          f'<p><span class="ex-q">As variáveis:</span> a barra clara é a banda '
          f'medida no <b>ciclo absoluto</b> — a que alimenta o piso publicado; a '
          f'sólida é a mesma banda em <b>vida normalizada</b> (cada réplica na '
          f'sua própria fração de vida). Só famílias com razão de duração '
          f'&le;&nbsp;{_RAZAO_DUR_MAX:.0f}×.</p>'
          f'<p><span class="ex-q">Como ler:</span> a parte <b>clara que sobra</b> '
          f'é erro que não existe no experimento — vem de comparar no mesmo ciclo '
          f'curvas que rodaram comprimentos diferentes, onde a curta já terminou '
          f'e a longa está no meio da vida.</p>'
          f'<p><span class="ex-q">Leitura do dado atual:</span> pior caso '
          f'<b>{_esc.escape(str(pior[1]))}</b>, com <b>{100 * pior[0]:.0f} %</b> '
          f'da banda vindo da duração; <b>{n_perde}</b> de {len(ok_dur)} famílias '
          f'perdem mais de 30 % ao normalizar.</p>'
          + (f'<p><span class="ex-q">Fora do gráfico</span> — razão de duração '
             f'&gt;&nbsp;{_RAZAO_DUR_MAX:.0f}×, onde normalizar por vida também '
             f'não tem sentido: '
             + " · ".join(f"<b>{_esc.escape(f)}</b> {rz:.1f}×"
                          for f, _n, rz, _ba, _bn in
                          sorted(fora_dur, key=lambda q: -q[2])) + '.</p>'
             if fora_dur else '')
          + f'</div>{_svg_barras_par(rows1)}')

    g2 = (f'<h3>Custo × qualidade do dado</h3>'
          f'<div class="explica">'
          f'<p><span class="ex-q">As variáveis:</span> no eixo x a <b>banda</b> '
          f'da fonte (o que as réplicas dela não distinguem, escala log); no y o '
          f'número de <b>constantes</b> que os configs daquela fonte carregam.</p>'
          f'<p><span class="ex-q">Como ler:</span> uma alocação racional desceria '
          f'da esquerda para a direita — <b>dado bom merece constante; dado que '
          f'não discrimina, não</b>. Pontos no alto à direita são constantes '
          f'gastas onde o experimento não decide.</p>'
          f'<p><span class="ex-q">Leitura do dado atual:</span> a alocação segue '
          f'a <b>dificuldade de ajustar</b>, não a qualidade do dado — é o achado '
          f'do <code>robustez_rotas_medidas.md</code>, aqui desenhado.</p></div>'
          f'{_svg_xy(pts2, "banda do dado (log)", "constantes", logx=True)}')

    g3 = (f'<h3>Procedência das constantes por curva</h3>'
          f'<div class="explica">'
          f'<p><span class="ex-q">As variáveis:</span> por fonte, quantas '
          f'entradas <code>(token, campo)</code> de <code>per_case</code> têm '
          f'procedência declarada (sólido) contra o total (claro).</p>'
          f'<p><span class="ex-q">Como ler:</span> um número por curva é '
          f'legítimo quando é <b>lido</b> — o <code>fat_C1</code> do LIU_2025 é a '
          f'vida N_f do paper — e é fit quando é <b>ajustado</b>. Os dois moram '
          f'no mesmo dict; a barra clara que sobra é a parte em que a página '
          f'<b>não sabe dizer qual é qual</b>.</p>'
          f'<p><span class="ex-q">Leitura do dado atual:</span> '
          f'<b>{sum(com_prov.values())}</b> de <b>{tot3}</b> entradas com '
          f'procedência ({100 * sum(com_prov.values()) / max(tot3, 1):.0f} %); as '
          f'demais são dívida contável, não erro.</p></div>'
          f'{_svg_barras_par(rows3)}')
    return g1 + g2 + g3


def _svg_barras_par(rows, w: int = 560, lw: int = 150, rw: int = 96) -> str:
    """Barra CHEIA = total, barra SOLIDA dentro = a parte que sobrevive.

    `rows` = [(rotulo, parte, total, nota)]. Desenha o total em tom fraco e a
    parte por cima, solida — a leitura e' "quanto do que se publica e' real".

    ⚠️ NAO reusa `_svg_barh`: aquele tem a semantica de "curvas FORA" cozida no
    tooltip (*"{v} de {tot} fora"*) e no `aria-label`, e emite `data-barh`, que
    o JS seleciona com `q('svg[data-barh]')` — seletor de UM elemento. Reusar
    daria rotulo mentiroso E roubaria a ligacao do painel ao vivo.
    """
    if not rows:
        return ""
    bh, gap = 15, 7
    h = len(rows) * (bh + gap) + 6
    vmax = max(tot for _l, _p, tot, _n in rows) or 1.0
    out = []
    for i, (lab, parte, tot, nota) in enumerate(rows):
        y = i * (bh + gap) + 3
        bt = (w - lw - rw) * tot / vmax
        bp = (w - lw - rw) * parte / vmax
        frac = parte / tot if tot else 0.0
        out.append(
            f'<text x="{lw - 6}" y="{y + bh - 3}" text-anchor="end" '
            f'class="tk">{_esc.escape(str(lab))}</text>'
            f'<rect x="{lw}" y="{y}" width="{max(bt, 1.0):.1f}" height="{bh}" '
            f'rx="3" style="fill:var(--mut);fill-opacity:.22"><title>'
            f'{_esc.escape(str(lab))}: total {tot:.4f}</title></rect>'
            f'<rect x="{lw}" y="{y}" width="{max(bp, 1.0):.1f}" height="{bh}" '
            f'rx="3" style="fill:var(--accent);fill-opacity:.85"><title>'
            f'{_esc.escape(str(lab))}: {parte:.4f} de {tot:.4f} '
            f'({frac:.0%} sobrevive)</title></rect>'
            f'<text x="{lw + bt + 6:.1f}" y="{y + bh - 3}" class="tk">'
            f'{_esc.escape(str(nota))}</text>')
    return (f'<svg viewBox="0 0 {w} {h}" class="plot" role="img" '
            f'aria-label="parte que sobrevive contra o total, por linha">'
            f'{"".join(out)}</svg>')


def _svg_xy(pts, xlab: str, ylab: str, w: int = 560, h: int = 300,
            logx: bool = False) -> str:
    """Dispersao generica rotulada. `pts` = [(x, y, rotulo)].

    ⚠️ Sem `data-s3`: o painel ao vivo liga-se por `q('svg[data-s3]')`, seletor
    de UM elemento, e um segundo grafico com o marcador dirigiria os controles
    para o alvo errado.
    """
    if not pts:
        return ""
    import math
    ML, MR, MT, MB = 52, 16, 14, 42
    xs = [(math.log10(max(x, 1e-6)) if logx else x) for x, _y, _r in pts]
    ys = [y for _x, y, _r in pts]
    x0, x1 = min(xs), max(xs)
    y0, y1 = 0.0, max(ys) * 1.08 or 1.0
    if x1 - x0 < 1e-12:
        x1 = x0 + 1.0
    X = lambda v: ML + (v - x0) / (x1 - x0) * (w - ML - MR)
    Y = lambda v: MT + (1 - v / y1) * (h - MT - MB)
    out = []
    for g in range(5):
        ty = y1 * g / 4
        tx = x0 + (x1 - x0) * g / 4
        rot = f"{10 ** tx:.3g}" if logx else f"{tx:.3g}"
        # ancora do ULTIMO tick em `end`: com `middle` ele vaza o viewBox
        # (medido: 570 num viewBox de 560), e SVG corta em silencio.
        anc = "end" if g == 4 else ("start" if g == 0 else "middle")
        out.append(f'<line x1="{ML}" y1="{Y(ty):.1f}" x2="{w - MR}" '
                   f'y2="{Y(ty):.1f}" class="gl"/>'
                   f'<text x="{ML - 6}" y="{Y(ty) + 3:.1f}" text-anchor="end" '
                   f'class="tk">{ty:.3g}</text>'
                   f'<text x="{X(tx):.1f}" y="{h - MB + 14}" '
                   f'text-anchor="{anc}" class="tk">{rot}</text>')
    for x, y, rot in pts:
        vx = math.log10(max(x, 1e-6)) if logx else x
        out.append(
            f'<circle cx="{X(vx):.1f}" cy="{Y(y):.1f}" r="4.5" '
            f'style="fill:var(--accent);fill-opacity:.8"><title>'
            f'{_esc.escape(str(rot))}: {xlab} {x:.4g} · {ylab} {y:.4g}</title>'
            f'</circle>'
            # rotulo a ESQUERDA na metade direita: a direita ele vazaria o
            # viewBox e o ponto de maior interesse (a fonte que mais gasta
            # constante) ficaria sem nome.
            + (f'<text x="{X(vx) - 7:.1f}" y="{Y(y) + 3:.1f}" '
               f'text-anchor="end" class="tk">{_esc.escape(str(rot))}</text>'
               if X(vx) > ML + 0.62 * (w - ML - MR) else
               f'<text x="{X(vx) + 7:.1f}" y="{Y(y) + 3:.1f}" class="tk">'
               f'{_esc.escape(str(rot))}</text>'))
    out.append(f'<text x="{(ML + w - MR) / 2:.0f}" y="{h - 6}" '
               f'text-anchor="middle" class="tk">{_esc.escape(xlab)}</text>'
               f'<text x="12" y="{(MT + h - MB) / 2:.0f}" class="tk" '
               f'transform="rotate(-90 12 {(MT + h - MB) / 2:.0f})" '
               f'text-anchor="middle">{_esc.escape(ylab)}</text>')
    return (f'<svg viewBox="0 0 {w} {h}" class="plot" role="img" '
            f'aria-label="{_esc.escape(ylab)} contra {_esc.escape(xlab)}">'
            f'{"".join(out)}</svg>')


# Limiares de retencao das normas. NAO sao a regua do tripe — sao a decisao de
# engenharia que o software de fato entrega ao usuario, e e outra pergunta.
_NORMAS = ((0.85, "ISO 16130:2015"), (0.80, "DIN 25201-4"))


def falso_seguro(res, lim: float = 0.85) -> bool:
    """O modelo diz que a junta RETEM e o ensaio diz que afrouxou.

    E o unico erro do modelo com consequencia de engenharia: falso ALARME custa
    dinheiro, falso SEGURO custa a junta. Lido no ponto final dos vetores da
    metrica — nunca da curva crua, que e' pre-alinhamento.
    """
    d = getattr(res, "metric_data", None)
    p_ = getattr(res, "metric_pred", None)
    if not (d and p_):
        return False
    return float(d[-1]) < lim <= float(p_[-1])


def _decisao_html(comp, results, pisos) -> str:
    """A matriz de decisao ISO/DIN — o que o tripe NAO mede.

    ⚠️ Por que esta secao existe: medido em 2026-08-25, **3 curvas aprovadas
    pelo tripe** informam retencao acima do limiar onde o ensaio mede abaixo. A
    `rousseau2025_hdpe_t10_amp0p2` tem MAE 0,0260 — fidelidade excelente — e
    diria "87 %" onde o dado mostra 80 %. O tripe mede fidelidade de CURVA; ele
    nao mede acerto de DECISAO, e os dois podem discordar. Nao e defeito do
    tripe: e uma pergunta que ele nao faz.
    """
    cens = [r for r in comp if caso_comparavel(r.source, r.case_id)]
    linhas, fs_nom = [], []
    for lim, norma in _NORMAS:
        vp = vn = fa = fs = 0
        for r in cens:
            res = results.get(r.case_id)
            if res is None:
                continue
            d = getattr(res, "metric_data", None)
            p_ = getattr(res, "metric_pred", None)
            if not (d and p_):
                continue
            o, m = float(d[-1]), float(p_[-1])
            if o < lim and m < lim:
                vp += 1
            elif o >= lim and m >= lim:
                vn += 1
            elif o >= lim > m:
                fa += 1
            else:
                fs += 1
                if abs(lim - 0.85) < 1e-9:
                    ok = _tripe_ok(res, limite_sres(r.source, pisos))
                    fs_nom.append((r.case_id, r.source, o, m, bool(ok)))
        n = vp + vn + fa + fs
        linhas.append(
            f'<tr><td>{norma}</td><td class="n">{lim:.0%}</td>'
            f'<td class="n">{(vp+vn)/max(n,1):.1%}</td>'
            f'<td class="n">{fa}</td><td class="n"><b>{fs}</b></td></tr>')
    if not fs_nom:
        return ""
    fs_nom.sort(key=lambda q: q[3] - q[2], reverse=True)
    n_tri = sum(1 for x in fs_nom if x[4])
    nomes = "".join(
        f'<tr><td><a href="reports/{_esc.escape(c)}.html"><code>'
        f'{_esc.escape(c)}</code></a></td><td class="n">{o:.3f}</td>'
        f'<td class="n">{m:.3f}</td><td class="n">{m-o:+.3f}</td>'
        f'<td>{"<b>SIM</b>" if ok else "não"}</td></tr>'
        for c, _s, o, m, ok in fs_nom)
    return (
        f'<h3>A decisão de engenharia — o que o tripé não mede</h3>'
        f'<table><tr><th>norma</th><th>limiar</th><th>acerto</th>'
        f'<th>falso alarme</th><th>falso SEGURO</th></tr>'
        f'{"".join(linhas)}</table>'
        f'<div class="explica">'
        f'<p><span class="ex-q">As variáveis:</span> a classificação que o '
        f'software entrega ao usuário — a junta <b>retém</b> acima do limiar da '
        f'norma, ou não? Lida no ponto final dos vetores da métrica.</p>'
        f'<p><span class="ex-q">Como ler:</span> os dois erros <b>não são '
        f'simétricos</b>. Falso <b>alarme</b> (diz que afrouxa e não afrouxou) '
        f'custa dinheiro; falso <b>SEGURO</b> (diz que retém e afrouxou) custa a '
        f'junta. Só um é perigoso.</p>'
        f'<p><span class="ex-q">Leitura do dado atual:</span> '
        f'<b>{len(fs_nom)}</b> falsos seguros no limiar da ISO 16130, e '
        f'⚠️ <b>{n_tri} deles PASSAM o tripé</b>.</p>'
        f'<p><span class="ex-q">⚠️ Por que isto não é defeito do tripé:</span> o '
        f'tripé mede fidelidade de <b>curva</b>; ele não mede acerto de '
        f'<b>decisão</b>. A primeira da lista tem MAE excelente e mesmo assim '
        f'informaria retenção acima do limiar onde o ensaio mede abaixo. É uma '
        f'pergunta que a régua não faz — e a marca abaixo é '
        f'<b>informacional</b>, no mesmo estatuto da deriva β: não muda '
        f'veredito. Promover a 4ª perna é decisão do professor (ITEM AB).</p>'
        f'</div>'
        f'<table><tr><th>curva</th><th>dado</th><th>modelo</th><th>Δ</th>'
        f'<th>passa o tripé?</th></tr>{nomes}</table>')


def _condicao_html(comp, results, pisos) -> str:
    """A secao "Por CONDICAO, nao por curva" — 3D estatico + censo + leitura.

    Segue a regra do projeto para todo grafico: **variaveis, como ler, e a
    leitura do dado ATUAL calculada na geracao** (nunca numero fixo em prosa).
    """
    pontos, solos, barradas = condicoes_agregadas(comp, results, pisos)
    if not pontos:
        return ""
    n_cond_ok = sum(1 for m, x, s, _r, lim, _n in pontos
                    if x <= META_MAX and m <= META_MAE and s <= lim)
    solo_ok = 0
    for cid in solos:
        res = results.get(cid)
        src = next((r.source for r in comp if r.case_id == cid), "")
        if res is not None and _tripe_ok(res, limite_sres(src, pisos)):
            solo_ok += 1
    tot = len(pontos) + len(solos)
    okk = n_cond_ok + solo_ok
    n_repl = sum(n for *_x, n in pontos)
    pts3 = [(m, x, s, r, lim) for m, x, s, r, lim, _n in pontos]
    bar = "".join(
        f"<li><b>{_esc.escape(f)}</b> — {n} curvas, razão de duração "
        f"<b>{rz:.0f}×</b></li>" for f, n, rz in sorted(barradas, key=lambda q: -q[2]))
    return (
        f'<h3>Por CONDIÇÃO, não por curva</h3>'
        f'<p class="sub2">Uma fonte com 6 réplicas pesava <b>6×</b> na nuvem e no '
        f'censo; aqui ela pesa <b>1</b>. As <b>{n_repl}</b> curvas que formam '
        f'condição com réplica colapsam em <b>{len(pontos)}</b> pontos, somadas às '
        f'<b>{len(solos)}</b> que ficam sozinhas ⇒ <b>{tot}</b> unidades de '
        f'julgamento em vez de {len(comp)} curvas.</p>'
        f'<div class="explica">'
        f'<p><span class="ex-q">As variáveis:</span> os mesmos três eixos do 3D '
        f'acima — MAE, resíduo máximo e σ_res — mas calculados sobre o resíduo '
        f'da <b>condição</b>: <code>média(previsões) − média(dados)</code> na '
        f'janela comum da família. O limite do σ_res segue o da fonte (D1).</p>'
        f'<p><span class="ex-q">Como ler:</span> cada ponto é uma condição '
        f'experimental, não uma corrida. A diferença entre este gráfico e o de '
        f'cima é <b>quanto do erro publicado era espalhamento entre réplicas</b> '
        f'— o erro contra uma réplica cobra do modelo a dispersão daquela '
        f'réplica, e o erro contra a condição não.</p>'
        f'<p><span class="ex-q">Leitura do dado atual:</span> <b>{okk} de {tot}</b> '
        f'unidades no tripé ({100.0 * okk / max(tot, 1):.0f} %), contra '
        f'<b>{sum(1 for r in comp if results.get(r.case_id) is not None and _tripe_ok(results[r.case_id], limite_sres(r.source, pisos)))}'
        f' de {len(comp)}</b> por curva. Das condições colapsadas, '
        f'<b>{n_cond_ok} de {len(pontos)}</b> passam.</p>'
        f'<p><span class="ex-q">⚠️ Isto NÃO é a porta:</span> o veredito publicado '
        f'segue por <b>curva</b>, e a razão está medida. Quando as 2 provas de '
        f'piso do <code>ECCLES</code> voltaram para a fila em 2026-08-23, foi '
        f'essa pressão que produziu o <code>arrest_approach_exp</code> — res.máx '
        f'0,1320 → <b>0,0488</b>. Uma leitura por condição usada como porta teria '
        f'"aprovado" as duas em 0,0851 e ninguém teria procurado a física. É a 2ª '
        f'instância do precedente D-M.</p>'
        + (f'<p><span class="ex-q">Famílias BARRADAS pela guarda de duração '
           f'(&gt;{_RAZAO_DUR_MAX:.0f}×):</span> comparar curvas de durações muito '
           f'diferentes no ciclo absoluto infla a banda — medido, 55–65 % em 4 '
           f'condições. Estas ficam como curvas soltas:</p><ul>{bar}</ul>'
           if bar else '')
        + f'</div>'
        f'{_svg_scatter3(pts3, omitidas=0, interativo=False)}')


def condicoes_agregadas(comp, results, pisos):
    """1 ponto por CONDICAO em vez de 1 por curva — sem sobreajuste de replica.

    Pedido do professor (2026-08-23): *"ajuste o relatorio de validacao e o
    grafico 3d para as condicoes sem sobreajuste das replicas"*. Uma fonte com 6
    replicas pesava **6x** na nuvem e no censo; aqui ela pesa **1**.

    O residuo da condicao e `media(previsoes) - media(dados)` na janela COMUM,
    que e' a leitura que a §1 do `erro_contra_condicao_vs_replica.md` mediu: o
    erro contra a replica cobra do modelo o espalhamento da propria replica.

    ⚠️ **Isto NAO e' a porta.** O veredito publicado segue por CURVA — e a razao
    esta medida: quando as 2 provas do ECCLES voltaram para a fila, foi essa
    pressao que produziu o `arrest_approach_exp` (res.max 0,1320 -> 0,0488). Uma
    leitura por condicao usada como porta teria "aprovado" as duas em 0,0851 e
    ninguem teria procurado a fisica.

    Devolve `(pontos, solos, barradas)`:
      · `pontos`  = [(mae, mx, sd, rotulo, lim_sd, n_curvas)] por condicao
      · `solos`   = case_ids que ficaram sozinhos (sem familia valida)
      · `barradas`= [(fonte, n, razao)] barradas pela guarda de duracao
    """
    import collections
    import numpy as np
    _vc = {r.case_id: r.validation_case for r in all_records()}
    fonte = {r.case_id: r.source for r in comp}
    gr = collections.defaultdict(list)
    V = {}
    for r in comp:
        cid = r.case_id
        res = results.get(cid)
        if res is None:
            continue
        x = getattr(res, "metric_x", None)
        d = getattr(res, "metric_data", None)
        pr = getattr(res, "metric_pred", None)
        if not (x and d and pr and len(x) == len(d) == len(pr) >= 4):
            continue
        V[cid] = (np.asarray(x, float), np.asarray(d, float), np.asarray(pr, float))
        cfg = getattr(res, "config_used", None) or {}
        if (cid in _SEM_FAMILIA_MECANICA
                and r.source not in _FONTES_RESOLVIDAS_POR_CHAVE):
            gr[("SOLO", cid)].append(cid)
            continue
        try:
            k = (r.source, round(float(cfg.get("delta_mm") or 0), 4),
                 round(float(cfg.get("F_amp_N") or 0), 1), cfg.get("mode"))
        except (TypeError, ValueError):
            gr[("SOLO", cid)].append(cid)
            continue
        vc = _vc.get(cid)
        if vc is not None:
            k = k + tuple(getattr(vc, campo, None) for campo in _CAMPOS_VARRIDOS)
        gr[k].append(cid)

    pontos, solos, barradas = [], [], []
    for k, cids in gr.items():
        if len(cids) < 2:
            solos.append(cids[0])
            continue
        dur = [V[c][0].max() for c in cids]
        razao = max(dur) / max(min(dur), 1e-9)
        if razao > _RAZAO_DUR_MAX:
            barradas.append((fonte.get(cids[0], k[0]), len(cids), float(razao)))
            solos.extend(cids)
            continue
        lo = max(V[c][0].min() for c in cids)
        hi = min(dur)
        if hi <= lo:
            solos.extend(cids)
            continue
        g = np.linspace(lo, hi, 60)
        D = np.array([np.interp(g, V[c][0], V[c][1]) for c in cids])
        P = np.array([np.interp(g, V[c][0], V[c][2]) for c in cids])
        r_ = P.mean(axis=0) - D.mean(axis=0)
        src = fonte.get(cids[0], k[0])
        rot = f"{src} ({len(cids)} repl.)"
        pontos.append((float(np.abs(r_).mean()), float(np.abs(r_).max()),
                       float(r_.std(ddof=1)), rot, limite_sres(src, pisos),
                       len(cids)))
    return pontos, solos, barradas


def _svg_scatter3(pts, w: int = 560, h: int = 510,
                  caps=(0.30, 0.60, 0.10), omitidas: int = 0,
                  lims=(META_MAE, META_MAX, META_SRES),
                  zlabel: str = "σ_res", interativo: bool = True) -> str:
    """MAE × res.máx × **3ª perna** em projeção axonométrica — o gráfico do
    gargalo em 3D (pedido de 2026-07-29). SVG puro; os controles ao vivo
    redesenham este mesmo bloco via JS, e sem JS ele fica no estado inicial.

    `pts` = [(mae, maxerr, z, rótulo)] · `caps` = teto de CADA eixo (o σ_res
    vive em 0–0.10 e o res.máx em 0–0.60: um teto comum esconderia a 3ª perna
    inteira dentro de 1,7 % do eixo) · `lims` = os três limites do tripé, que
    formam a **caixa de aceitação** — ela não é um cubo, porque as três pernas
    não têm o mesmo valor.

    Duas leituras que só o 3D dá:

    · **A caixa é o tripé.** Estar dentro dela é a aprovação; a projeção mostra
      *por qual face* cada curva saiu.
    · **A sombra cinza no plano da frente (z=0) é exatamente o gráfico 2D
      anterior** — desenhada para o olho não perder a referência de onde cada
      curva estava antes de a 3ª perna existir.

    Com `zlabel="RMSE"` o eixo de profundidade vira o RMSE, e aí vale a nota da
    cunha: as três normas-p do mesmo resíduo (p = 1, 2, ∞) obedecem
    `MAE <= RMSE <= res.máx` sempre, logo um limite no RMSE nunca reprova quem
    passa no res.máx — nesse modo o eixo é LEITURA (posição na cunha: perto do
    MAE = erro espalhado; perto do res.máx = concentrado em picos), não porta.

    **Três limitações desta vista, MEDIDAS no render real de 2026-07-29** (as
    duas primeiras foram consertadas, a terceira não tem conserto nesta escala).
    Os números abaixo saem de contar pixels no SVG emitido para as 202 curvas do
    store, não de estimar pela fórmula dos eixos:

    1. as **104 curvas aprovadas** ocupavam **2.68 %** da área útil do gráfico
       ⇒ metade do dado num canto ilegível. O modo "×limite" do seletor (só com
       JS) reprojeta em múltiplos do limite com escala raiz e leva isso a
       **9.81 %** — **3.66× mais área** —, e nada é recortado, porque o pior
       múltiplo medido é 8.86× e o teto comum vira 9×;
    2. a profundidade estava a 12.5° do eixo principal da nuvem — ver `_ROT3`;
    3. mesmo em "×limite", a **densidade dentro da caixa continua alta**:
       distância mediana ao vizinho entre as aprovadas 1.72 px → 2.90 px
       (1.69×), e **88 das 104 seguem a menos de 6 px** de outra, que é o
       diâmetro da marca. As curvas aprovadas *são* concentradas perto da
       origem, e nenhuma escala conserta isso — o que conserta é o leitor de
       foco (hover/foco preenche `#s3-info`) ou a tabela de casos, que lista as
       202 com link.
    """
    if not pts:
        return ""
    # MT=58 (era 34) para caber a BARRA DA RAMPA na 2ª linha do cabeçalho COM os
    # rótulos dela acima da barra; h=452 (era 420) para a altura útil do gráfico
    # não pagar pelo cabeçalho (Hp fica igual ao de antes: 348/1.30 = 267.7).
    # Orçamento vertical medido: linha 1 em MT-40, rótulos da rampa em MT-25,
    # barra em MT-22..MT-14, topo do gráfico em MT. Com MT=46 os rótulos da
    # rampa caíam sobre a linha 1 — foi o que a captura mostrou.
    # 2026-08-01: MT 58->84 e h 452->478 JUNTOS, para a área útil não pagar pela
    # 3ª linha do cabeçalho — `Hp = h-MT-MB` continua 348, igual ao de antes.
    # Novo orçamento vertical: linha 1 em MT-66, rótulos da rampa em MT-51,
    # barra em MT-48..MT-40, CHAVE DE FORMAS em MT-18, topo do gráfico em MT.
    # MB 46->78 e h 478->510 em 2026-08-07 (Hp segue 348): as DUAS notas do
    # rodape precisavam de faixa propria. Antes elas caiam por cima dos
    # tiques do eixo x (y0+13) e do rotulo MAE — a captura mostrou, a
    # varredura NAO, porque ela so' checava colisao no CABECALHO.
    # Orcamento do rodape: tiques em y0+13, MAE em y0+30, nota das
    # omitidas em h-30, nota de recorte em h-14.
    ML, MR, MT, MB = 46, 16, 84, 78
    cx, cy, cz = (float(c) if c else 1.0 for c in caps)
    lx_, ly_, lz_ = (float(v) for v in lims)
    DX, DY = _ROT3                   # encurtamento do eixo de profundidade
    Wp = (w - ML - MR) / (1.0 + DX)
    Hp = (h - MT - MB) / (1.0 + DY)
    y0 = MT + Hp * (1.0 + DY)        # canto (0,0,0), frente-baixo-esquerda
    cl = lambda v, c: min(max(float(v), 0.0), c) / c

    def P(a, b, c):
        u, v, z = cl(a, cx), cl(b, cy), cl(c, cz)
        return (ML + u * Wp + z * DX * Wp, y0 - v * Hp - z * DY * Hp)

    def ln(p, q, cls="gl", extra=""):
        return (f'<line x1="{p[0]:.1f}" y1="{p[1]:.1f}" x2="{q[0]:.1f}" '
                f'y2="{q[1]:.1f}" class="{cls}"{extra}/>')

    gx, gy, gz = (_mult_grade(cx, lx_), _mult_grade(cy, ly_),
                  _mult_grade(cz, lz_))
    out = []
    # --- caixa do domínio: piso (res.máx=0), parede esquerda (MAE=0) e face da
    #     frente (z=0). Piso e parede ficam ESPARSOS (0/meio/teto) de propósito:
    #     a grade fina vale onde se lêem x e y, que é a face da frente.
    for f in (0.0, 0.5, 1.0):
        out.append(ln(P(f * cx, 0, 0), P(f * cx, 0, cz)))     # piso, profundidade
        out.append(ln(P(0, 0, f * cz), P(cx, 0, f * cz)))     # piso, largura
        out.append(ln(P(0, f * cy, 0), P(0, f * cy, cz)))     # parede esquerda
    out.append(ln(P(0, 0, 0), P(cx, 0, 0)))                   # eixos em zero
    out.append(ln(P(0, 0, 0), P(0, cy, 0)))
    for i, v in enumerate(gy):                                # face da frente
        out.append(ln(P(0, v, 0), P(cx, v, 0)))
        # o tique do LIMITE sai na cor da perna: é onde a cor do ponto vira
        cor = ' style="fill:var(--warn)"' if i == 0 else ''
        out.append(f'<text x="{P(0, v, 0)[0] - 6:.1f}" '
                   f'y="{P(0, v, 0)[1] + 3:.1f}" text-anchor="end" '
                   f'class="tk"{cor}>{v:.4g}</text>')
    for i, v in enumerate(gx):
        out.append(ln(P(v, 0, 0), P(v, cy, 0)))
        cor = ' style="fill:var(--di)"' if i == 0 else ''
        out.append(f'<text x="{P(v, 0, 0)[0]:.1f}" y="{y0 + 13:.1f}" '
                   f'text-anchor="middle" class="tk"{cor}>{v:.4g}</text>')
    # --- CAIXA DE ACEITAÇÃO: o tripé é um volume, e de arestas DESIGUAIS
    a_, b_, c_ = min(lx_, cx), min(ly_, cy), min(lz_, cz)
    face = [P(0, 0, 0), P(a_, 0, 0), P(a_, b_, 0), P(0, b_, 0)]
    out.append('<polygon data-box="frente" points="'
               + " ".join(f"{x:.1f},{y:.1f}" for x, y in face)
               + '" style="fill:var(--good);fill-opacity:.13"/>')
    topo = [P(0, b_, 0), P(a_, b_, 0), P(a_, b_, c_), P(0, b_, c_)]
    out.append('<polygon data-box="topo" points="'
               + " ".join(f"{x:.1f},{y:.1f}" for x, y in topo)
               + '" style="fill:var(--good);fill-opacity:.07"/>')
    for p, q in ((P(a_, 0, 0), P(a_, b_, 0)), (P(0, b_, 0), P(a_, b_, 0)),
                 (P(a_, b_, 0), P(a_, b_, c_)), (P(0, b_, c_), P(a_, b_, c_)),
                 (P(a_, 0, c_), P(a_, b_, c_)), (P(0, b_, 0), P(0, b_, c_)),
                 (P(a_, 0, 0), P(a_, 0, c_)), (P(0, 0, c_), P(a_, 0, c_)),
                 (P(0, 0, c_), P(0, b_, c_))):
        out.append(ln(p, q, "rl", ' stroke-dasharray="4 3"'))
    # --- pontos: longe (z alto) primeiro, para o painter's algorithm valer
    fora_teto = []
    # Contagem por FORMA, acumulada no mesmo laço que desenha — a chave do
    # cabeçalho publica estes números. Contar aqui e não numa varredura à parte
    # é o que garante que a legenda conte exatamente o que foi desenhado.
    cont_forma = {"reg": 0, "exc": 0, "decl": 0, "rec": 0}
    for a, b, c, lab, *resto in sorted(pts, key=lambda t: -t[2]):
        # 5º elemento opcional = limite efetivo da 3ª perna DESTA curva (D1,
        # piso por fonte). Ausente => global (os testes usam 4-tuplas).
        lzi = float(resto[0]) if resto else lz_
        rec = a > cx or b > cy or c > cz
        if rec:
            fora_teto.append((max(a / cx, b / cy, c / cz), lab))
        # cor = a RAMPA (modo default). O modo "perna que manda"
        # (`_COR_PERNA[_perna_manda(...)]`) é oferecido pelo seletor, que é JS —
        # o desenho estático fica no default, como todo o resto da página.
        cor = _cor_rampa(_severidade(a, b, c, lx_, ly_, lzi))
        px, py = P(a, b, c)
        sx, sy = P(a, b, 0)                               # sombra no plano 2D
        out.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="1.6" '
                   f'style="fill:var(--mut);fill-opacity:.25"/>')
        # a haste liga o ponto à própria sombra: é o que faz o olho ler
        # profundidade em vez de ver duas nuvens sobrepostas. A .18 do 1º
        # desenho era invisível na tela (medido em captura), .34 lê.
        out.append(ln((sx, sy), (px, py), "gl",
                      ' stroke-opacity=".34"'))
        # LINK DE VERDADE (`<a>` do SVG), não `window.open` num handler: em
        # `file://` o navegador trata `window.open` como popup e BLOQUEIA — era
        # o "erro ao clicar no caso" de 2026-07-29, e ele não aparecia sobre
        # http://, só no modo em que a página é de fato usada. De quebra, o link
        # funciona SEM JS (o SVG do Python não tinha link nenhum antes),
        # aceita clique do meio e "abrir em nova aba".
        # `tabindex="-1"`: 202 links dentro de um SVG viram ARMADILHA DE TECLADO
        # (202 paradas de tab antes do resto da página). A rota acessível
        # equivalente é a tabela de casos, que lista as mesmas 202 com link.
        # `data-cid` vai no `<a>`, não na marca: quem delega o hover procura
        # `closest('a[data-cid]')` e assim funciona igual para o círculo e para
        # o triângulo de recorte.
        out.append(
            f'<a href="reports/{_esc.escape(str(lab))}.html" target="_blank" '
            f'rel="noopener" tabindex="-1" '
            f'data-cid="{_esc.escape(str(lab))}">'
            f'{_marca3(px, py, cor, rec, _cont_forma(cont_forma, str(lab), rec))}'
            f'<title>{_esc.escape(str(lab))} — '
            f'MAE {a:.3f} · res.máx {b:.3f} · {zlabel} {c:.4g}'
            f'{_ROT_ESTATUTO.get(estatuto_da_curva(str(lab)), "")}'
            f'{" — RECORTADO na borda" if rec else ""}'
            f' — clique abre o report</title></a>')
    # --- eixo de profundidade: marcas + rótulo. Sem os tiques o 3º eixo seria
    #     só uma direção, não uma escala — não se leria o valor de um ponto.
    #     O rótulo vai CENTRADO no meio da aresta (com âncora no meio): posto na
    #     ponta com âncora inicial, o texto rotacionado saía do viewBox.
    for i, v in enumerate(gz):
        bx, by = P(cx, 0, v)
        out.append(ln((bx, by), (bx + 4, by + 4)))
        # ACIMA-À-ESQUERDA da aresta, âncora no fim. Duas armadilhas medidas:
        # com âncora inicial o tique da ponta (x=544 de 560) saía 10 px do
        # viewBox; e ABAIXO da aresta o 1º múltiplo colidia com o último tique do
        # eixo x (sobreposição de 9.9 × 2.7 px, detectada por varredura de
        # `getBBox` na página, não a olho). Acima-à-esquerda cai na região
        # `res.máx < MAE`, que é VAZIA POR TEOREMA (`MAE <= res.máx` sempre) —
        # o mesmo argumento que escolhe a direção da profundidade.
        # Rótulo só no limite e no teto quando a grade tem mais de 3 marcas.
        if len(gz) <= 3 or i in (0, len(gz) - 1):
            out.append(f'<text x="{bx - 6:.1f}" y="{by - 4:.1f}" '
                       f'text-anchor="end" class="tk" '
                       f'style="fill:var(--accent)">{v:.4g}</text>')
    # Rótulo do 3º eixo HORIZONTAL, na ponta da aresta e com âncora no fim
    # (antes: rotacionado ao longo da aresta, com âncora no meio). Duas razões:
    # com a profundidade íngreme o texto rotacionado caía EM CIMA do tique do
    # primeiro múltiplo, e o ângulo muda quando o usuário gira — um rótulo cuja
    # legibilidade depende da rotação é um rótulo que quebra no uso.
    # −20 (não −9) porque os tiques do 3º eixo agora ficam ACIMA da aresta e a
    # −9 o rótulo encostava no do teto; o `min` com y0−20 impede que ele desça
    # para o rodapé quando o usuário gira a profundidade para BAIXO (dy < 0).
    zty = min(P(cx, 0, cz)[1] - 20.0, y0 - 20.0)
    out.append(f'<text x="{(ML + w - MR) / 2:.0f}" y="{y0 + 30:.0f}" '
               f'text-anchor="middle" class="axl" '
               f'style="fill:var(--di)">MAE</text>'
               f'<text x="13" y="{(MT + y0) / 2:.0f}" text-anchor="middle" '
               f'class="axl" style="fill:var(--warn)" transform="rotate(-90 13 '
               f'{(MT + y0) / 2:.0f})">resíduo máximo</text>'
               f'<text x="{w - MR:.0f}" y="{zty:.1f}" text-anchor="end" '
               f'class="axl" style="fill:var(--accent)">'
               f'{_esc.escape(zlabel)} ↗</text>')
    # Linha 1 ENCURTADA em 2026-08-01: a frase da sombra saiu daqui e virou uma
    # entrada da chave de formas. Medido antes do corte: a linha terminava em
    # x=597 num viewBox de 560, ou seja **53 px cortados** — e o corte só doía
    # no render ESTÁTICO (impressão/PDF/sem-JS), porque o JS já emitia a versão
    # curta. Era divergência Python-vs-JS somada a texto invisível.
    out.append(f'<text x="{ML}" y="{MT - 66}" class="tk" '
               f'style="fill:var(--mut)">caixa tracejada = o tripé '
               f'(MAE {lx_:.4g} · res.máx {ly_:.4g} · {_esc.escape(zlabel)} '
               f'{lz_:.4g}) · uma linha de grade = um limite</text>')
    out.append(_legenda_rampa(ML, MT - 48))
    out.append(_legenda_formas(ML, MT - 18, cont_forma))
    # AS DUAS NOTAS DO RODAPÉ (revisão 2026-08-07). Antes havia só a de
    # recorte, e ela CONTRADIZIA a chave de formas do cabeçalho: o rodapé
    # contava TODA curva recortada e escrevia "▲ N", enquanto a chave contava
    # só as que de fato viram triângulo — e o triângulo perde para o estatuto
    # (losango/quadrado vencem). Com uma recortada que também é exceção, o
    # mesmo desenho exibia dois números para a mesma coisa. Agora o rodapé diz
    # a REPARTIÇÃO, que é o que ensina a regra em vez de esconder o conflito.
    if omitidas:
        # Curva sem σ_res julgável (n<6 pontos, regra assinada 2026-08-01) não
        # tem coordenada de profundidade e não pode ser desenhada. Omitir em
        # silêncio faria a chave ("declarada 7") contradizer as tabelas
        # ("declaradas 12") sem explicação visível.
        out.append(f'<text x="{ML}" y="{h - 30}" class="tk" '
                   f'style="fill:var(--mut)">{omitidas} curva'
                   f'{"s" if omitidas > 1 else ""} sem σ_res julgável '
                   f'(n&lt;6 pontos) fora deste gráfico — sem 3ª perna não há '
                   f'profundidade; elas estão nas tabelas</text>')
    if fora_teto:
        # RODAPÉ, não cabeçalho: no cabeçalho esta nota colidia com a legenda da
        # caixa, que é longa (medido em captura). Aqui divide a linha com o
        # rótulo "MAE", que é centrado, e sobra folga.
        pior = max(fora_teto)
        _tri = sum(1 for _m, _lab in fora_teto
                   if not estatuto_da_curva(str(_lab)))
        out.append(f'<text x="{w - MR}" y="{h - 14}" text-anchor="end" '
                   f'class="tk" style="fill:var(--mut)">'
                   f'{len(fora_teto)} recortada(s) na borda (pior '
                   f'{pior[0]:.1f}× o teto) — ▲ em {_tri}; '
                   f'{len(fora_teto) - _tri} mantém a forma do estatuto'
                   f'</text>')
    # ⚠️ `data-s3` e o SELETOR do painel ao vivo, e o JS usa
    # `q('svg[data-s3]')` — seletor de UM elemento. Um segundo 3D na mesma
    # pagina com esse marcador roubaria a ligacao do primeiro (ou seria
    # ignorado, dependendo da ordem no DOM), e o painel de controles ficaria
    # dirigindo o grafico errado. Dai `interativo=False` para o 3D por
    # CONDICAO: ele e estatico DE PROPOSITO, na rotacao padrao.
    return (f'<svg viewBox="0 0 {w} {h}" class="plot" role="img" '
            + (f'data-s3="1" ' if interativo else '')
            + f'data-cx="{cx:.6g}" data-cy="{cy:.6g}" '
            f'data-cz="{cz:.6g}" data-ml="{ML}" data-mt="{MT}" '
            f'data-wp="{Wp:.4f}" data-hp="{Hp:.4f}" data-y0="{y0:.4f}" '
            f'data-dx="{DX}" data-dy="{DY}" data-zlab="{_esc.escape(zlabel)}" '
            f'data-w="{w}" data-h="{h}" data-mr="{MR}" data-mb="{MB}" '
            f'data-omit="{omitidas}" '
            f'aria-label="dispersão 3D: MAE × resíduo máximo × '
            f'{_esc.escape(zlabel)}">{"".join(out)}</svg>')


def _marca3(px: float, py: float, cor: str, recortado: bool,
            estatuto: str = "") -> str:
    """A marca de um ponto do 3D. **A FORMA carrega o ESTATUTO** (pedido do
    professor, 2026-08-01) — sem isso o gráfico afirmava que exceção e
    declarada são a mesma coisa que uma curva medida contra a régua:

    · **círculo** — julgada pela régua (no tripé ou fora dela por mérito);
    · **losango** — EXCEÇÃO assinada (o erro está provado ≤ o piso do dado);
    · **quadrado** — DECLARADA (a métrica ou o dado não decidem a curva).

    `recortado` **não rouba mais a forma** (correção de 2026-08-01, medida no
    render): com o triângulo vencendo, **16 dos 35 pontos com estatuto**
    perdiam a marca no modo absoluto — 7 das 9 declaradas viravam triângulo e
    o pedido "exceção tem de parecer diferente" ficava meio atendido. Agora o
    recorte é um **contorno escuro** sobre a forma do estatuto: os dois fatos
    (o que a curva é · o ponto não está onde aparece) usam canais visuais
    diferentes e cabem juntos. Sem sinal nenhum, um res.máx 0.66 desenhado em
    cima da borda de 0.60 lê-se como se valesse 0.60 (medido 2026-07-29: 3
    curvas, a pior a 1.1× do teto).

    Triângulo continua existindo para a curva **sem estatuto** recortada — é a
    convenção que a nota do canto (▲) usa e que já estava no leitor.

    `cor` é uma cor CSS completa (`#rrggbb` da rampa ou `var(--x)` do modo
    discreto)."""
    ct = (';stroke:var(--ink);stroke-width:1.2;stroke-opacity:.85'
          if recortado else '')
    if estatuto == "exc":       # losango
        return (f'<polygon points="'
                f'{px:.1f},{py - 4.0:.1f} {px + 4.0:.1f},{py:.1f} '
                f'{px:.1f},{py + 4.0:.1f} {px - 4.0:.1f},{py:.1f}" '
                f'style="cursor:pointer;fill:{cor};fill-opacity:.88{ct}"/>')
    if estatuto == "decl":      # quadrado
        return (f'<rect x="{px - 2.8:.1f}" y="{py - 2.8:.1f}" '
                f'width="5.6" height="5.6" '
                f'style="cursor:pointer;fill:{cor};fill-opacity:.88{ct}"/>')
    if recortado:               # sem estatuto + recortado = triângulo (▲)
        return (f'<polygon points="'
                f'{px:.1f},{py - 4.2:.1f} {px + 3.8:.1f},{py + 2.6:.1f} '
                f'{px - 3.8:.1f},{py + 2.6:.1f}" '
                f'style="cursor:pointer;fill:{cor};fill-opacity:.92"/>')
    return (f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3" '
            f'style="cursor:pointer;fill:{cor};fill-opacity:.85"/>')


def estatuto_da_curva(cid: str) -> str:
    """`"exc"` (exceção assinada) · `"decl"` (declarada) · `""` (julgada pela
    régua). Uma função só, lida pelo SVG do Python E pelo payload do JS, para
    a forma do marcador não poder divergir entre o desenho estático e o
    interativo."""
    if cid in _EXCECOES:
        return "exc"
    if cid in _DECLARADAS:
        return "decl"
    return ""


# Largura média de caractere em `class="tk"` (9px) MEDIDA no render, não
# estimada: `getBBox` sobre os rótulos reais do painel dá ~4.62 px/caractere.
# Serve só para o Python posicionar itens numa linha — o SVG não sabe medir
# texto, e sem isto a chave de formas só poderia ser conferida depois de
# desenhada. A varredura de `getBBox` continua sendo o juiz.
_CHAR_TK = 4.62


def _cont_forma(cont, cid: str, rec: bool) -> str:
    """Devolve o estatuto de `cid` E o contabiliza na classe da FORMA que ele
    vai receber.

    A classe é a da marca desenhada, não a do estatuto: `recortada` só ganha o
    triângulo quando não há estatuto (a forma do estatuto vence — correção de
    2026-08-01). Contar pelo estatuto daria uma legenda que promete triângulos
    que o gráfico não desenha."""
    est = estatuto_da_curva(cid)
    if est:
        cont[est] = cont.get(est, 0) + 1
    elif rec:
        cont["rec"] = cont.get("rec", 0) + 1
    else:
        cont["reg"] = cont.get("reg", 0) + 1
    return est


def _legenda_formas(x: float, y: float, cont) -> str:
    """Chave das FORMAS do 3D, desenhada com `_marca3` — a MESMA função que
    desenha os pontos do gráfico.

    Por que reusar `_marca3` em vez de escrever os glifos ●◆■▲ como texto: uma
    legenda que redesenha a marca por conta própria pode divergir do gráfico, e
    **divergiu de fato** (medido 2026-08-01: a linha 1 do Python citava a sombra
    e a do JS não). Reusando a função, a chave não é uma *descrição* da marca —
    é a marca.

    Por que dentro do SVG e não só na prosa abaixo: o vocabulário de formas
    existia apenas no bloco `_explica`, a uma rolagem de distância, com glifos
    de texto que o leitor tinha de casar de cabeça com o desenho. Chave de
    símbolo pertence ao gráfico; é o único lugar onde ela é lida no momento em
    que a dúvida aparece — e é o que sai na impressão junto com o desenho.

    `cont` = contagens vivas por classe, para a chave dizer também *quanto* de
    cada coisa existe hoje."""
    itens = [("", False, "julgada pela régua", cont.get("reg", 0)),
             ("exc", False, "exceção", cont.get("exc", 0)),
             ("decl", False, "declarada", cont.get("decl", 0)),
             ("", True, "recortada", cont.get("rec", 0))]
    out, cur = [], x
    for est, rec, rot, n in itens:
        if not n:
            continue                      # classe vazia não vira entrada morta
        txt = f"{rot} {n}"
        out.append(_marca3(cur + 4, y - 3, "var(--mut)", rec, est))
        out.append(f'<text x="{cur + 11:.1f}" y="{y:.1f}" class="tk" '
                   f'style="fill:var(--mut)">{txt}</text>')
        cur += 11 + len(txt) * _CHAR_TK + 14
    # a sombra fecha a chave: é o único elemento do desenho que NÃO é uma curva,
    # e sem dizer isso o leitor conta 2× os pontos (a marca e a sombra dela).
    out.append(f'<circle cx="{cur + 4:.1f}" cy="{y - 3:.1f}" r="1.6" '
               f'style="fill:var(--mut);fill-opacity:.45"/>')
    out.append(f'<text x="{cur + 11:.1f}" y="{y:.1f}" class="tk" '
               f'style="fill:var(--mut)">sombra no piso (z=0)</text>')
    return "".join(out)


def _legenda_rampa(x: float, y: float, n: int = 26) -> str:
    """Barra da rampa como legenda: `n` retângulos em vez de um
    `<linearGradient>` num `<defs>`.

    Motivo de não usar `defs`: o mesmo desenho é reconstruído por
    `innerHTML` no JS a cada giro/limite, e `innerHTML` em SVG com `defs`
    referenciado por `url(#id)` é frágil (ids duplicados quando há mais de um
    gráfico na página). 26 retângulos são o desenho literal, idêntico nas duas
    implementações, e imprimem igual."""
    bw = 4.2
    # Rótulo CURTO de propósito: a versão longa ("distância à origem (modelo
    # perfeito), em múltiplos do limite:") empurrava a barra para x=304 e a nota
    # "▲ N recortada(s)" colidia com ela na mesma linha — medido em captura.
    # O significado do 1× está no bloco de explicação, que é o lugar dele.
    out = [f'<text x="{x:.1f}" y="{y + 7:.1f}" class="tk" '
           f'style="fill:var(--mut)">distância à origem (×limite):</text>']
    x0 = x + 132
    for i in range(n):
        d = _RAMPA_TETO * i / (n - 1)
        out.append(f'<rect x="{x0 + i * bw:.1f}" y="{y:.1f}" '
                   f'width="{bw + 0.4:.1f}" height="8" '
                   f'style="fill:{_cor_rampa(d)}"/>')
    for f, txt in ((0.0, "0"), (1.0 / _RAMPA_TETO, "1× = a caixa"),
                   (1.0, f"{_RAMPA_TETO:.0f}×")):
        out.append(f'<text x="{x0 + f * (n - 1) * bw + bw / 2:.1f}" '
                   f'y="{y - 3:.1f}" text-anchor="middle" class="tk" '
                   f'style="fill:var(--mut)">{txt}</text>')
    return "".join(out)


# Camada interativa do painel "Onde está o erro" (2026-07-29).
# ENHANCEMENT PROGRESSIVO, e isso é requisito, não estilo: o Python já emitiu os
# SVGs corretos nos limites padrão, então sem JS (impressão, PDF, leitor
# restrito) a página continua íntegra — este script só RECOLORE e REPROJETA o
# que já está lá.
# A projeção axonométrica está duplicada aqui em 3 linhas (`P()`), porque girar
# exige reprojetar; o INVARIANTE é que ela leia os mesmos DX/DY/Wp/Hp/y0 que o
# Python publicou nos `data-*` do próprio SVG — nunca constantes próprias.
_JS_PAINEL = r"""
(function(){
  var D = window.__BAS3__ || [], DEF = window.__BAS3DEF__ || {};
  if (!D.length) return;
  var q = function(s){ return document.querySelector(s); };
  var inMx = q('#in-mx'), inMae = q('#in-mae'), inSd = q('#in-sd'),
      inZ = q('#in-z'), inE = q('#in-esc'), inC = q('#in-cor'),
      bt = q('#bt-reset'),
      inExc = q('#in-exc'), inDecl = q('#in-decl');
  if (!inMx) return;
  var s3 = q('svg[data-s3]');
  var rot = {dx: s3 ? +s3.dataset.dx : 0.08, dy: s3 ? +s3.dataset.dy : 0.30};
  var ROT0 = {dx: rot.dx, dy: rot.dy};
  // filtro por ESTATUTO (pedido 2026-08-07): tira da VISTA, nunca da
  // contagem — a chave declara 'N ocultas' para a omissao ser visivel.
  var VER = {exc: true, decl: true};
  var L = {mx: +inMx.value, mae: +inMae.value, sd: +inSd.value};
  var ZMODE = 'd';                 // qual métrica no eixo de profundidade
  var ESC = 'abs';                 // escala: 'abs' | 'lim' (múltiplos, √)
  var CMODE = inC ? inC.value : 'grad';   // cor: 'grad' | 'perna' | 'tripe'
  var ZLAB = {d: 'σ_res', r: 'RMSE', b: '|viés|'};

  function fmt(v){ return (Math.round(v*10000)/10000).toString(); }
  function zval(c){ return ZMODE === 'd' ? c.d : (ZMODE === 'r' ? c.r : c.b); }
  // D1 (piso por fonte): o limite EFETIVO da 3a perna e' max(slider, piso da
  // fonte). O slider segue sendo o limite GLOBAL (subir afrouxa tudo); `pf` so
  // existe no payload quando a flag esta ligada E o piso excede o global —
  // sem ele, tudo se comporta exatamente como antes.
  function lsd(c){ return Math.max(L.sd, c.pf || 0); }
  function ok3(c){
    return c.x <= L.mx && c.a <= L.mae && c.d !== null && c.d <= lsd(c);
  }
  // teto do eixo de profundidade: p98 do que está no ar, arredondado para uma
  // escala legível — teto fixo esconderia a perna quando o modo troca
  function capZ(){
    var v = D.map(zval).filter(function(z){ return z !== null; }).sort(
      function(a,b){ return a-b; });
    if (!v.length) return 0.1;
    var p = v[Math.floor(0.98*(v.length-1))];
    var esc = [0.02,0.05,0.1,0.15,0.2,0.3,0.5,0.6,1.0];
    for (var i=0;i<esc.length;i++){ if (esc[i] >= p) return esc[i]; }
    return 1.0;
  }

  function contas(){
    var n = D.length, nok = 0, som = 0, sox = 0, sos = 0;
    var porf = {};
    D.forEach(function(c){
      var o = ok3(c);
      if (o) nok++;
      var bm = c.a > L.mae, bx = c.x > L.mx,
          bs = (c.d === null || c.d > L.sd);
      if (bm && !bx && !bs) som++;
      if (bx && !bm && !bs) sox++;
      if (bs && !bm && !bx) sos++;
      porf[c.s] = porf[c.s] || [0,0];
      porf[c.s][1]++;
      if (!o) porf[c.s][0]++;
    });
    return {n:n, ok:nok, som:som, sox:sox, sos:sos, porf:porf};
  }

  function pinta(){
    var r = contas();
    var set = function(id, v){ var e = q(id); if (e) e.textContent = v; };
    set('#tri-n', r.ok); set('#tri-fora', r.n - r.ok);
    var f100 = 0, nf = 0;
    for (var k in r.porf){ nf++; if (!r.porf[k][0]) f100++; }
    set('#tri-f100', f100);
    set('#lv-mx', fmt(L.mx)); set('#lv-mae', fmt(L.mae));
    set('#lv-sd', fmt(L.sd));
    q('#ou-mx').value = fmt(L.mx); q('#ou-mae').value = fmt(L.mae);
    q('#ou-sd').value = fmt(L.sd);
    // --- histogramas: só cor das barras + posição da linha do limite
    [['mae', L.mae], ['mx', L.mx], ['sd', L.sd]].forEach(function(p){
      var sv = q('svg[data-hist="' + p[0] + '"]');
      if (!sv) return;
      var st = +sv.dataset.step, ml = +sv.dataset.ml, pw = +sv.dataset.pw;
      sv.querySelectorAll('rect[data-lo]').forEach(function(b){
        var lo = +b.dataset.lo, hi = +b.dataset.hi;
        // mesma regra do Python: a faixa CORTADA pelo limite não é verde nem
        // vermelha, é meia — senão o olho conta aprovadas que não existem
        var meia = lo < p[1] && p[1] < hi;
        b.style.fill = 'var(--' + ((lo >= p[1] || meia) ? 'warn' : 'good') + ')';
        b.style.fillOpacity = meia ? '.45' : '.8';
      });
      var x = ml + (p[1]/st) * pw;
      var li = sv.querySelector('line[data-lim]');
      if (li){ li.setAttribute('x1', x.toFixed(1));
               li.setAttribute('x2', x.toFixed(1)); }
      var tx = sv.querySelector('text[data-limtxt]');
      if (tx){ tx.setAttribute('x', (x+4).toFixed(1));
               tx.textContent = 'limite ' + fmt(p[1]); }
    });
    // --- barras por fonte: o conjunto muda com os limites, então redesenha
    var bh = q('svg[data-barh]');
    if (bh){
      var lw = +bh.dataset.lw, rw = +bh.dataset.rw, H = +bh.dataset.bh,
          gp = +bh.dataset.gap, W = +bh.dataset.w;
      var rows = [];
      for (var s in r.porf){ if (r.porf[s][0]) rows.push([s, r.porf[s][0], r.porf[s][1]]); }
      rows.sort(function(a,b){ return b[1]-a[1] || (a[0]<b[0]?-1:1); });
      var vmax = rows.length ? rows[0][1] : 1, o = [];
      rows.forEach(function(rw2, i){
        var y = i*(H+gp)+3, bl = (W-lw-rw)*rw2[1]/vmax;
        o.push('<text x="'+(lw-6)+'" y="'+(y+H-3)+'" text-anchor="end" class="tk">'
          + rw2[0] + '</text><rect x="'+lw+'" y="'+y+'" width="'+Math.max(bl,1).toFixed(1)
          + '" height="'+H+'" rx="3" style="fill:var(--warn);fill-opacity:.85"></rect>'
          + '<text x="'+(lw+bl+6).toFixed(1)+'" y="'+(y+H-3)+'" class="tk">'
          + rw2[1] + '/' + rw2[2] + '</text>');
      });
      bh.setAttribute('viewBox', '0 0 ' + W + ' ' + (rows.length*(H+gp)+6));
      bh.innerHTML = o.join('');
    }
    desenha3();
  }

  // --- ESCALA de um eixo. `f(v)` leva o valor bruto a [0,1] da aresta.
  //     'abs' = linear ate o teto (o desenho historico).
  //     'lim' = MULTIPLOS DO LIMITE com escala RAIZ. Duas coisas de uma vez:
  //       (a) as tres pernas passam a ter a MESMA unidade ("x o limite"), logo
  //           a caixa de aceitacao vira um CUBO e distancia visual igual =
  //           severidade igual — que e' exatamente a pergunta do painel;
  //       (b) a raiz descomprime o canto denso. MEDIDO no render (contando
  //           pixels, nao pela formula): as 104 aprovadas saem de 2.68% para
  //           9.81% da area util (3.66x), vizinho mediano 1.72 -> 2.90 px, e com
  //           teto comum de 9x NADA e' recortado (pior multiplo do store 8.86x).
  //           Em LINEAR o mesmo teto daria ~1.2% — PIOR que o absoluto; e' a
  //           raiz que faz o trabalho, nao a normalizacao sozinha.
  //       Limite honesto: 88 das 104 aprovadas seguem a menos de 6 px (o
  //       diametro da marca) de outra. A concentracao e' do dado.
  function eixo(cap, lim, raiz){
    var t = raiz && lim > 0
      ? function(v){ return Math.sqrt(v/lim); }
      : function(v){ return v; };
    var tc = t(cap) || 1;
    return {cap: cap, lim: lim, raiz: !!(raiz && lim > 0),
            f: function(v){ return t(Math.min(Math.max(v,0),cap))/tc; }};
  }
  // Marcas: multiplos INTEIROS do limite (a 1a e' o limite, e coincide com a
  // aresta da caixa) — em 'lim' o rotulo e' "kx", em 'abs' o valor absoluto.
  function marcas(ax, mult){
    var r = [], k, i;
    if (ax.lim > 0 && ax.cap/ax.lim <= 8.51){
      k = Math.max(1, Math.round(ax.cap/ax.lim));
      for (i=1;i<=k;i++) r.push([i*ax.cap/k, mult ? i+'×' : null]);
    } else if (ax.lim > 0 && mult){
      k = Math.max(1, Math.round(ax.cap/ax.lim));
      [1,2,4,6,9,12,16,25].forEach(function(m){
        if (m <= k) r.push([m*ax.lim, m+'×']); });
      if (!r.length) r.push([ax.cap, k+'×']);
    } else {
      for (i=1;i<=4;i++) r.push([i*ax.cap/4, null]);
    }
    return r;
  }
  // teto comum em multiplos do limite, no modo 'lim': o menor da escala que
  // cobre TUDO, para nao existir ponto recortado neste modo
  function capMult(lz){
    var m = 0;
    D.forEach(function(c){
      var z = zval(c);
      m = Math.max(m, c.a/L.mae, c.x/L.mx,
                   (lz > 0 && z !== null) ? z/lz : 0);
    });
    var e = [1,2,3,4,6,9,12,16,25,36], i;
    for (i=0;i<e.length;i++){ if (e[i] >= m) return e[i]; }
    return Math.ceil(m);
  }

  function desenha3(){
    if (!s3) return;
    var ML = +s3.dataset.ml, MT = +s3.dataset.mt, Wp = +s3.dataset.wp,
        Hp = +s3.dataset.hp, y0 = +s3.dataset.y0;
    var DX = rot.dx, DY = rot.dy;
    // A 3a perna so tem LIMITE no modo σ_res; RMSE e |vies| nao tem porta
    // declarada, e por isso o seletor de escala 'lim' forca ZMODE='d' (ver o
    // handler): "multiplos de um limite que nao existe" nao significa nada.
    var lz = (ZMODE === 'd') ? L.sd : 0;
    var MU = ESC === 'lim', cm = MU ? capMult(lz) : 0;
    var ex = MU ? eixo(cm*L.mae, L.mae, 1) : eixo(+s3.dataset.cx, L.mae, 0),
        ey = MU ? eixo(cm*L.mx,  L.mx,  1) : eixo(+s3.dataset.cy, L.mx,  0),
        ez = MU ? eixo(cm*(lz||1), lz, 1) : eixo(capZ(), lz, 0);
    var cx = ex.cap, cy = ey.cap, cz = ez.cap;
    var P = function(a,b,c){
      return [ML + ex.f(a)*Wp + ez.f(c)*DX*Wp,
              y0 - ey.f(b)*Hp - ez.f(c)*DY*Hp];
    };
    var ln = function(p,q2,cls,ex2){
      return '<line x1="'+p[0].toFixed(1)+'" y1="'+p[1].toFixed(1)+'" x2="'
        + q2[0].toFixed(1)+'" y2="'+q2[1].toFixed(1)+'" class="'+(cls||'gl')+'" '
        + (ex2||'')+'/>';
    };
    var o = [], f, i;
    for (i=0;i<3;i++){ f = i/2;
      o.push(ln(P(f*cx,0,0), P(f*cx,0,cz)));
      o.push(ln(P(0,0,f*cz), P(cx,0,f*cz)));
      o.push(ln(P(0,f*cy,0), P(0,f*cy,cz)));
    }
    o.push(ln(P(0,0,0), P(cx,0,0)));
    o.push(ln(P(0,0,0), P(0,cy,0)));
    marcas(ey, MU).forEach(function(m, j){
      o.push(ln(P(0,m[0],0), P(cx,m[0],0)));
      var pa = P(0,m[0],0);
      o.push('<text x="'+(pa[0]-6).toFixed(1)+'" y="'+(pa[1]+3).toFixed(1)
        + '" text-anchor="end" class="tk"'
        + (j===0 ? ' style="fill:var(--warn)"' : '') + '>'
        + (m[1] || fmt(m[0])) + '</text>');
    });
    marcas(ex, MU).forEach(function(m, j){
      o.push(ln(P(m[0],0,0), P(m[0],cy,0)));
      o.push('<text x="'+P(m[0],0,0)[0].toFixed(1)+'" y="'+(y0+13).toFixed(1)
        + '" text-anchor="middle" class="tk"'
        + (j===0 ? ' style="fill:var(--di)"' : '') + '>'
        + (m[1] || fmt(m[0])) + '</text>');
    });
    // caixa de aceitação: em modo σ_res a 3ª aresta é o limite; nos outros
    // modos a perna não tem limite, então a caixa vira LAJE (vai até o teto)
    var a_ = Math.min(L.mae,cx), b_ = Math.min(L.mx,cy),
        c_ = lz ? Math.min(lz,cz) : cz;
    var poly = function(pts, op){
      return '<polygon points="' + pts.map(function(p){
        return p[0].toFixed(1)+','+p[1].toFixed(1); }).join(' ')
        + '" style="fill:var(--good);fill-opacity:'+op+'"/>';
    };
    o.push(poly([P(0,0,0),P(a_,0,0),P(a_,b_,0),P(0,b_,0)], '.13'));
    o.push(poly([P(0,b_,0),P(a_,b_,0),P(a_,b_,c_),P(0,b_,c_)], '.07'));
    [[P(a_,0,0),P(a_,b_,0)],[P(0,b_,0),P(a_,b_,0)],[P(a_,b_,0),P(a_,b_,c_)],
     [P(0,b_,c_),P(a_,b_,c_)],[P(a_,0,c_),P(a_,b_,c_)],[P(0,b_,0),P(0,b_,c_)],
     [P(a_,0,0),P(a_,0,c_)],[P(0,0,c_),P(a_,0,c_)],[P(0,0,c_),P(0,b_,c_)]
    ].forEach(function(e){ o.push(ln(e[0],e[1],'rl','stroke-dasharray="4 3"')); });
    var pts = D.slice().filter(function(c){ return zval(c) !== null; })
                .sort(function(p,r2){ return zval(r2)-zval(p); });
    var fora = [];
    var CF = {reg:0, exc:0, decl:0, rec:0}, OC = {exc:0, decl:0};
  pts.forEach(function(c){
      // filtro de estatuto: fora da VISTA (nem sombra, nem recorte, nem
      // rodape), mas contado em OC para a chave declarar a ocultacao
      if (c.e === 'exc' && !VER.exc){ OC.exc++; return; }
      if (c.e === 'decl' && !VER.decl){ OC.decl++; return; }
      var z = zval(c), rec = c.a > cx || c.x > cy || z > cz;
      if (rec) fora.push([Math.max(c.a/cx, c.x/cy, z/cz), c.c, c.e||'']);
      // classe da FORMA desenhada (o estatuto vence o recorte, igual ao
      // Python `_cont_forma`) — a chave publica exatamente o que foi desenhado
      if (c.e === 'exc') CF.exc++; else if (c.e === 'decl') CF.decl++;
      else if (rec) CF.rec++; else CF.reg++;
      var pp = P(c.a,c.x,z), sh = P(c.a,c.x,0), cor = corDe(c);
      o.push('<circle cx="'+sh[0].toFixed(1)+'" cy="'+sh[1].toFixed(1)
        + '" r="1.6" style="fill:var(--mut);fill-opacity:.25"/>');
      o.push(ln(sh,pp,'gl','stroke-opacity=".34"'));
      // <a> de verdade, igual ao que o Python emite: window.open e' bloqueado
      // como popup quando a pagina abre em file://. tabindex=-1 tira 202
      // paradas de tab do caminho do teclado (a tabela de casos e' a rota
      // acessivel equivalente).
      o.push('<a href="reports/'+c.c+'.html" target="_blank" rel="noopener" '
        + 'tabindex="-1" data-cid="'+c.c+'">'
        + marca(pp[0], pp[1], cor, rec, c.e)
        + '<title>'+c.c+' — MAE '+c.a+' · res.máx '+c.x+' · '+ZLAB[ZMODE]+' '+z
        + (c.e === 'exc' ? ' — EXCEÇÃO assinada (◆)'
           : (c.e === 'decl' ? ' — DECLARADA (■)' : ''))
        + (rec ? ' — RECORTADO na borda' : '')
        + ' — clique abre o report</title></a>');
    });
    var mz = marcas(ez, MU);
    mz.forEach(function(m, j){
      var b2 = P(cx,0,m[0]);
      o.push(ln(b2,[b2[0]+4,b2[1]+4]));
      // acima-a-esquerda: abaixo da aresta o 1o multiplo colidia com o ultimo
      // tique do eixo x (medido por varredura de getBBox)
      if (mz.length <= 3 || j === 0 || j === mz.length-1)
        o.push('<text x="'+(b2[0]-6).toFixed(1)+'" y="'+(b2[1]-4).toFixed(1)
          + '" text-anchor="end" class="tk" style="fill:var(--accent)">'
          + (m[1] || fmt(m[0]))+'</text>');
    });
    var hh = +s3.getAttribute('viewBox').split(' ')[3];
    var ww = +s3.getAttribute('viewBox').split(' ')[2];
    // MAE acompanha o GRAFICO (y0+30), nao o fim do SVG: o rodape ganhou
    // faixa propria para as duas notas e o rotulo nao pode descer com ela.
    o.push('<text x="'+((ML+ww-16)/2).toFixed(0)+'" y="'+(y0+30).toFixed(0)
      + '" text-anchor="middle" class="axl" style="fill:var(--di)">MAE</text>');
    o.push('<text x="13" y="'+((MT+y0)/2).toFixed(0)+'" text-anchor="middle" '
      + 'class="axl" style="fill:var(--warn)" transform="rotate(-90 13 '
      + ((MT+y0)/2).toFixed(0)+')">resíduo máximo</text>');
    // rótulo do 3º eixo HORIZONTAL na ponta da aresta: rotacionado ao longo dela
    // ele colidia com o 1º tique e a legibilidade passava a depender do giro.
    // −20 e o `min` com y0−20: ver o comentário gêmeo no Python (tiques acima da
    // aresta + giro para baixo)
    o.push('<text x="'+(ww-16)+'" y="'
      + Math.min(P(cx,0,cz)[1]-20, y0-20).toFixed(1)+'" '
      + 'text-anchor="end" class="axl" style="fill:var(--accent)">'
      + ZLAB[ZMODE]+' ↗</text>');
    // Em ×limite a frase "uma linha de grade = um limite" é REDUNDANTE (os
    // tiques já dizem "1×, 2×…"), e mantê-la fazia a linha passar de x=622 num
    // viewBox de 560 — o texto era cortado. Uma frase por modo, nunca as duas.
    o.push('<text x="'+ML+'" y="'+(MT-66)+'" class="tk" style="fill:var(--mut)">'
      + 'caixa tracejada = o tripé (MAE '+fmt(L.mae)+' · res.máx '+fmt(L.mx)
      + (lz ? ' · σ_res '+fmt(L.sd) : ' · '+ZLAB[ZMODE]+' sem limite')
      + ') · ' + (MU
          ? 'eixos em múltiplos do limite (escala √, teto '+cm+'×)'
          : 'uma linha de grade = um limite')
      + '</text>');
    o.push(legenda(ML, MT-48));
  o.push(formas(ML, MT-18, CF, OC));
    // As DUAS notas, espelhando o Python (revisao 2026-08-07). A de recorte
    // agora REPARTE: o rodape contava toda curva recortada como "▲ N" e a
    // chave contava so' as que viram triangulo — e o triangulo perde para o
    // estatuto. O mesmo desenho mostrava dois numeros para a mesma coisa.
    var OMIT = +(s3.getAttribute('data-omit') || 0);
    if (OMIT){
      o.push('<text x="'+ML+'" y="'+(hh-30)+'" class="tk" '
        + 'style="fill:var(--mut)">'+OMIT+' curva'+(OMIT>1?'s':'')
        + ' sem σ_res julgável (n&lt;6 pontos) fora deste gráfico — sem 3ª '
        + 'perna não há profundidade; elas estão nas tabelas</text>');
    }
    if (fora.length){
      // rodapé, não cabeçalho: lá colidia com a legenda longa da caixa
      fora.sort(function(a,b){ return b[0]-a[0]; });
      var nTri = 0, k;
      for (k = 0; k < fora.length; k++) if (!fora[k][2]) nTri++;
      o.push('<text x="'+(ww-16)+'" y="'+(hh-16)+'" text-anchor="end" '
        + 'class="tk" style="fill:var(--mut)">'+fora.length
        + ' recortada(s) na borda (pior '+fora[0][0].toFixed(1)
        + '× o teto) — ▲ em '+nTri+'; '+(fora.length-nTri)
        + ' mantém a forma do estatuto</text>');
    }
    s3.innerHTML = o.join('');
    if (alvo) foca(alvo, true);        // o foco sobrevive ao redesenho
  }

  // --- cor = a perna que MANDA (o maior múltiplo estourado), espelhando
  //     `_perna_manda` do Python. Verde = passa nas três.
  function corPerna(c){
    var z = c.d, v = [], ls = lsd(c);
    if (c.a > L.mae) v.push([c.a/L.mae, 'di']);
    if (c.x > L.mx)  v.push([c.x/L.mx,  'warn']);
    if (z === null)  v.push([1/0, 'accent']);
    else if (z > ls) v.push([z/ls, 'accent']);
    if (!v.length) return 'good';
    v.sort(function(a,b){ return b[0]-a[0]; });
    return v[0][1];
  }
  // --- severidade: o MAIOR múltiplo de limite estourado. `<=1` <=> passa no
  //     tripé (a meta é uma conjunção, logo uma condição de norma-máximo), e é
  //     esta identidade que faz a rampa e a caixa nunca se contradizerem.
  //     A 3ª perna usa o limite EFETIVO da curva (D1) — senão a cor e o censo
  //     discordariam, que é a contradição que esta identidade proíbe.
  function sev(c){
    if (c.d === null) return 1/0;
    return Math.max(c.a/L.mae, c.x/L.mx, c.d/lsd(c));
  }
  // rampa verde->âmbar->vermelho, espelho exato de `_cor_rampa` do Python
  // (hexes fixos: interpolar exige número, e `--good` muda com o tema)
  var RAMPA = [[0x1f,0x9d,0x55],[0xe0,0xa4,0x11],[0xd1,0x3b,0x2e]], RTETO = 3;
  function corRampa(d){
    if (!(d >= 0)) d = RTETO;                       // NaN/Infinity => saturado
    var a = d <= 1 ? RAMPA[0] : RAMPA[1], b = d <= 1 ? RAMPA[1] : RAMPA[2],
        t = d <= 1 ? Math.min(Math.max(d,0),1) : Math.min((d-1)/(RTETO-1),1), s='#', i;
    for (i=0;i<3;i++){
      var v = Math.round(a[i] + (b[i]-a[i])*t).toString(16);
      s += v.length < 2 ? '0'+v : v;
    }
    return s;
  }
  // as duas codificações de cor: 'grad' = o MAX (quão longe da origem),
  // 'perna' = o ARGMAX (por qual perna), 'tripe' = o binário histórico
  function corDe(c){
    if (CMODE === 'grad') return corRampa(sev(c));
    if (CMODE === 'tripe') return ok3(c) ? 'var(--good)' : 'var(--warn)';
    return 'var(--' + corPerna(c) + ')';
  }
  // legenda: a barra da rampa (26 retângulos, igual ao Python) ou as 4 cores
  // discretas — o desenho tem de dizer o que a cor significa AGORA
  // Espelho de `_legenda_formas` do Python. As duas TEM de existir: o Python
  // desenha o estado inicial (impressao/PDF/sem-JS) e o JS redesenha a cada
  // giro. Foi a AUSENCIA de espelho que deixou a linha 1 divergir — o Python
  // citava a sombra, o JS nao, e a versao do Python era a que era cortada.
  function formas(x, y, cf, oc){
    var IT = [['', false, 'julgada pela régua', cf.reg],
              ['exc', false, 'exceção', cf.exc],
              ['decl', false, 'declarada', cf.decl],
              ['', true, 'recortada', cf.rec]];
    var o = [], cur = x, i, it, txt;
    for (i = 0; i < IT.length; i++){
      it = IT[i];
      if (!it[3]) continue;              // classe vazia nao vira entrada morta
      txt = it[2] + ' ' + it[3];
      o.push(marca(cur + 4, y - 3, 'var(--mut)', it[1], it[0]));
      o.push('<text x="' + (cur + 11).toFixed(1) + '" y="' + y
        + '" class="tk" style="fill:var(--mut)">' + txt + '</text>');
      cur += 11 + txt.length * 4.62 + 14;
    }
    // rotulo CURTO ('◆ 22 ocultas'): a versao longa ('◆ excecoes: 22
    // ocultas (filtro)') empurrava a entrada da sombra para fora do viewBox —
    // medido na varredura com o filtro ativo. O que ◆ significa ja esta
    // escrito no proprio checkbox que causou a ocultacao.
    var esc2 = [['exc','◆'], ['decl','■']], eo2;
    for (i = 0; i < esc2.length; i++){
      eo2 = esc2[i];
      if (!oc || !oc[eo2[0]]) continue;
      txt = eo2[1] + ' ' + oc[eo2[0]] + ' ocultas';
      o.push('<text x="' + (cur + 4).toFixed(1) + '" y="' + y
        + '" class="tk" style="fill:var(--mut);font-style:italic">'
        + txt + '</text>');
      cur += txt.length * 4.62 + 16;
    }
    o.push('<circle cx="' + (cur + 4).toFixed(1) + '" cy="' + (y - 3)
      + '" r="1.6" style="fill:var(--mut);fill-opacity:.45"/>');
    o.push('<text x="' + (cur + 11).toFixed(1) + '" y="' + y
      + '" class="tk" style="fill:var(--mut)">sombra no piso (z=0)</text>');
    return o.join('');
  }
  function legenda(x, y){
    var o = [], i, n = 26, bw = 4.2, x0 = x + 132;
    if (CMODE !== 'grad'){
      if (CMODE === 'tripe')
        return '<text x="'+x+'" y="'+(y+6)+'" class="tk">'
          + '<tspan style="fill:var(--good)">■ passa nas três pernas</tspan>'
          + '<tspan style="fill:var(--mut)"> · </tspan>'
          + '<tspan style="fill:var(--warn)">■ fora do tripé</tspan></text>';
      return '<text x="'+x+'" y="'+(y+6)+'" class="tk">'
        + '<tspan style="fill:var(--good)">■ passa nas três</tspan>'
        + '<tspan style="fill:var(--mut)"> · a cor de quem falha é a perna que '
        + 'manda: </tspan><tspan style="fill:var(--di)">■ MAE</tspan>'
        + '<tspan style="fill:var(--mut)"> · </tspan>'
        + '<tspan style="fill:var(--warn)">■ res.máx</tspan>'
        + '<tspan style="fill:var(--mut)"> · </tspan>'
        + '<tspan style="fill:var(--accent)">■ '+ZLAB[ZMODE]+'</tspan></text>';
    }
    // rótulo CURTO e sem frase de rodapé — a versão longa empurrava a barra
    // para fora e colidia com a nota de recorte (o significado do 1× está no
    // bloco de explicação, que é o lugar dele)
    o.push('<text x="'+x+'" y="'+(y+7)+'" class="tk" style="fill:var(--mut)">'
      + 'distância à origem (×limite):</text>');
    for (i=0;i<n;i++)
      o.push('<rect x="'+(x0+i*bw).toFixed(1)+'" y="'+y+'" width="'+(bw+0.4)
        + '" height="8" style="fill:'+corRampa(RTETO*i/(n-1))+'"/>');
    [[0,'0'],[1/RTETO,'1× = a caixa'],[1,RTETO+'×']].forEach(function(t){
      o.push('<text x="'+(x0+t[0]*(n-1)*bw+bw/2).toFixed(1)+'" y="'+(y-3)
        + '" text-anchor="middle" class="tk" style="fill:var(--mut)">'
        + t[1]+'</text>');
    });
    return o.join('');
  }
  // marca do ponto: triângulo quando RECORTADO no teto — desenhar um círculo em
  // cima da borda afirmaria um valor que não é o dado.
  // `cor` já vem COMPLETA ('#rrggbb' da rampa ou 'var(--x)' do modo discreto):
  // re-embrulhar em var(--...) gerava `fill:var(--#d13b2e)`, que o navegador
  // resolve como PRETO — foi o que pintou os 202 pontos de preto no 1º teste.
  // FORMA = ESTATUTO (2026-08-01): circulo = julgada pela regua, losango =
  // EXCECAO assinada, quadrado = DECLARADA. Precedencia: `rec` (recortado)
  // vence e vira triangulo — e' verdade sobre o DESENHO (o ponto nao esta
  // onde aparece), e ela tem de ganhar de qualquer rotulo. Espelha
  // `_marca3`/`estatuto_da_curva` do Python: as duas implementacoes leem o
  // MESMO estatuto (campo `e` do payload), entao nao podem divergir.
  function marca(px, py, cor, rec, est){
    var ct = rec ? ';stroke:var(--ink);stroke-width:1.2;stroke-opacity:.85'
                 : '';
    if (est === 'exc') return '<polygon points="'
      + px.toFixed(1)+','+(py-4.0).toFixed(1)+' '
      + (px+4.0).toFixed(1)+','+py.toFixed(1)+' '
      + px.toFixed(1)+','+(py+4.0).toFixed(1)+' '
      + (px-4.0).toFixed(1)+','+py.toFixed(1)
      + '" style="cursor:pointer;fill:'+cor+';fill-opacity:.88'+ct+'"/>';
    if (est === 'decl') return '<rect x="'+(px-2.8).toFixed(1)+'" y="'
      + (py-2.8).toFixed(1)+'" width="5.6" height="5.6"'
      + ' style="cursor:pointer;fill:'+cor+';fill-opacity:.88'+ct+'"/>';
    if (rec) return '<polygon points="'+px.toFixed(1)+','+(py-4.2).toFixed(1)
      + ' '+(px+3.8).toFixed(1)+','+(py+2.6).toFixed(1)+' '
      + (px-3.8).toFixed(1)+','+(py+2.6).toFixed(1)
      + '" style="cursor:pointer;fill:'+cor+';fill-opacity:.92"/>';
    return '<circle cx="'+px.toFixed(1)+'" cy="'+py.toFixed(1)
      + '" r="3" style="cursor:pointer;fill:'+cor+';fill-opacity:.85"/>';
  }

  // --- LEITOR DE FOCO. Com 202 pontos e distância mediana ao vizinho de 1.5 px
  //     medida, o `<title>` nativo (que só abre depois de ~1 s parado) não
  //     resolve uma curva individual. Este bloco dá o nome e as três réguas em
  //     MÚLTIPLOS do limite — a leitura que decide se a curva está perto ou
  //     longe de entrar — e diz qual perna manda.
  var IX = {}; D.forEach(function(c){ IX[c.c] = c; });
  var alvo = null, info = q('#s3-info');
  var NOME = {di:'MAE', warn:'res.máx', accent:'σ_res/3ª perna', good:'—'};
  function foca(cid, mantem){
    var el = s3 && s3.querySelector('a[data-cid="'+cid+'"]');
    if (el){
      var m = el.firstChild;
      m.style.fillOpacity = '1';
      m.style.stroke = 'var(--fg)'; m.style.strokeWidth = '1.3';
      if (m.tagName === 'circle') m.setAttribute('r', '5.2');
    }
    alvo = cid;
    var c = IX[cid];
    if (!info || !c) return;
    var mu = function(v, l){
      return v === null ? '—'
        : fmt(v) + ' <b>(' + (v/l).toFixed(2) + '×)</b>';
    };
    // O NOME DO CASO É O LINK para o report dele. Não é enfeite: os 202 links dos
    // pontos saíram da ordem de tab (armadilha de teclado), então este é o
    // caminho de teclado/leitor de tela para a mesma página que o clique abre.
    info.innerHTML = '<a href="reports/' + c.c + '.html" target="_blank" '
      + 'rel="noopener">' + c.c + '</a> · <span class="s3f">'
      + c.s + '</span> · MAE ' + mu(c.a, L.mae) + ' · res.máx ' + mu(c.x, L.mx)
      + ' · σ_res ' + mu(c.d, lsd(c))
      + (c.pf ? ' <span class="s3f">(limite da fonte ' + fmt(lsd(c))
                + ' — D1, piso medido)</span>' : '')
      + ' · RMSE ' + (c.r===null?'—':fmt(c.r))
      + ' · |viés| ' + (c.b===null?'—':fmt(c.b))
      + ' · perna que manda: <b>' + NOME[corPerna(c)] + '</b>';
    if (!mantem) info.dataset.on = '1';
  }
  function desfoca(){
    if (alvo && s3){
      var el = s3.querySelector('a[data-cid="'+alvo+'"]');
      if (el){ var m = el.firstChild;
        m.style.fillOpacity = m.tagName === 'circle' ? '.85' : '.92';
        m.style.stroke = ''; m.style.strokeWidth = '';
        if (m.tagName === 'circle') m.setAttribute('r', '3'); }
    }
    alvo = null;
    if (info) info.innerHTML = info.dataset.vazio || '';
  }

  // --- girar: arrastar dentro do 3D muda o encurtamento do eixo de
  //     profundidade. Limites evitam a degenerescência (dx→0 achata o eixo).
  if (s3){
    var arrastando = false, x0 = 0, y0d = 0, r0 = null, movimento = 0,
        pend = false;
    s3.style.cursor = 'grab';
    s3.style.touchAction = 'none';   // sem isto, no touch o gesto rola a página
    s3.setAttribute('tabindex', '0');
    // redesenho a 1 por quadro: o pointermove dispara ~10x mais que isso e
    // cada passada reconstrói ~1200 nós de SVG
    var agenda = function(){
      if (pend) return; pend = true;
      requestAnimationFrame(function(){ pend = false; desenha3(); });
    };
    var solta = function(){ arrastando = false; s3.style.cursor = 'grab'; };
    s3.addEventListener('pointerdown', function(e){
      arrastando = true; x0 = e.clientX; y0d = e.clientY; movimento = 0;
      r0 = {dx: rot.dx, dy: rot.dy}; s3.style.cursor = 'grabbing';
      // *** NAO chamar setPointerCapture aqui. ***
      // Com captura de ponteiro ativa o navegador RETARGETA o `click` para o
      // elemento que capturou (o <svg>) em vez do <a> sob o cursor, e o LINK DO
      // PONTO NUNCA ABRE. Foi exatamente o que aconteceu: a captura entrou como
      // conserto do "arrasto grudado" e matou o clique-para-abrir-o-report.
      // O arrasto grudado se resolve sem captura, com `e.buttons === 0` abaixo.
    });
    // pointermove na JANELA (não no SVG): sem captura, o SVG para de receber
    // eventos quando o cursor sai dele, e a rotação congelaria no meio do gesto.
    window.addEventListener('pointermove', function(e){
      if (!arrastando) return;
      // ARRASTO GRUDADO: soltar o botão fora da janela não gera pointerup. Na
      // primeira volta do cursor, `buttons === 0` denuncia que já foi solto.
      if (e.buttons === 0) { solta(); return; }
      movimento = Math.max(movimento,
        Math.abs(e.clientX - x0) + Math.abs(e.clientY - y0d));
      rot.dx = Math.min(0.62, Math.max(0.06, r0.dx + (e.clientX-x0)/900));
      // dy pode ficar NEGATIVO: a profundidade aponta para baixo-direita, que é
      // a direção ~ortogonal à nuvem (o semiplano res.máx < MAE é vazio POR
      // TEOREMA — `MAE <= res.máx` sempre —, então não há o que ocultar lá).
      rot.dy = Math.min(0.46, Math.max(-0.28, r0.dy - (e.clientY-y0d)/900));
      agenda();
    });
    ['pointerup','pointercancel'].forEach(function(ev){
      window.addEventListener(ev, solta);
    });
    window.addEventListener('blur', solta);
    // arrastar para girar nao pode virar clique no link. Limiar de 8 px na SOMA
    // |dx|+|dy|: com 4 px um tremor de mao durante o clique (3 em x + 2 em y)
    // ja cancelava a navegacao, e 8 px de arrasto mudam a rotacao em 0.009 —
    // invisivel. Barato de folgar, caro de apertar.
    s3.addEventListener('click', function(e){
      if (movimento > 8) { e.preventDefault(); e.stopPropagation(); }
    }, true);
    // girar pelo TECLADO (o SVG é focável): a rotação era só de mouse
    s3.addEventListener('keydown', function(e){
      var k = e.key, p = 0.03;
      if (k === 'ArrowRight') rot.dx = Math.min(0.62, rot.dx + p);
      else if (k === 'ArrowLeft') rot.dx = Math.max(0.06, rot.dx - p);
      else if (k === 'ArrowUp') rot.dy = Math.min(0.46, rot.dy + p);
      else if (k === 'ArrowDown') rot.dy = Math.max(-0.28, rot.dy - p);
      else return;
      e.preventDefault(); agenda();
    });
    s3.addEventListener('mouseover', function(e){
      var a = e.target.closest && e.target.closest('a[data-cid]');
      if (a && a.dataset.cid !== alvo){ desfoca(); foca(a.dataset.cid); }
    });
    s3.addEventListener('mouseleave', desfoca);
  }

  [inMx, inMae, inSd].forEach(function(el){
    el.addEventListener('input', function(){
      L.mx = +inMx.value; L.mae = +inMae.value; L.sd = +inSd.value; pinta();
    });
  });
  if (inZ) inZ.addEventListener('change', function(){
    ZMODE = inZ.value;
    // 'lim' mede em múltiplos DO LIMITE, e RMSE/|viés| não têm limite
    // declarado — a combinação não significa nada, então a escala volta p/ abs
    if (ZMODE !== 'd' && ESC === 'lim'){ ESC = 'abs'; if (inE) inE.value = 'abs'; }
    desenha3();
  });
  if (inE) inE.addEventListener('change', function(){
    ESC = inE.value;
    if (ESC === 'lim' && ZMODE !== 'd'){
      ZMODE = 'd'; if (inZ) inZ.value = 'd';
    }
    desenha3();
  });
  [[inExc,'exc'],[inDecl,'decl']].forEach(function(par){
    if (par[0]) par[0].addEventListener('change', function(){
      VER[par[1]] = par[0].checked; desenha3(); }); });
  if (inC) inC.addEventListener('change', function(){
    CMODE = inC.value; desenha3();
  });
  if (bt) bt.addEventListener('click', function(){
    L.mx = DEF.mx; L.mae = DEF.mae; L.sd = DEF.sd;
    inMx.value = DEF.mx; inMae.value = DEF.mae; inSd.value = DEF.sd;
    rot.dx = ROT0.dx; rot.dy = ROT0.dy;
    if (inZ){ inZ.value = 'd'; ZMODE = 'd'; }
    if (inE){ inE.value = 'abs'; ESC = 'abs'; }
    if (inC){ inC.value = 'grad'; CMODE = 'grad'; }
    if (inExc){ inExc.checked = true; } if (inDecl){ inDecl.checked = true; }
    VER.exc = VER.decl = true; desenha3();
    desfoca(); pinta();
  });
  if (info) info.dataset.vazio = info.innerHTML;
  pinta();
})();
"""


def _criterio_html(pisos: dict, n: int, n_imp_mae: int, n_imp_sd: int,
                   n_sd: int) -> str:
    """JUSTIFICATIVA TÉCNICA dos três limites, dentro da página (pedido do
    professor 2026-07-29: *"não esqueça de escrever uma justificativa técnica
    para esses valores no html"*).

    Regra que ela obedece: **o limite é uma DECISÃO (constante no código), o
    piso é uma MEDIÇÃO (recomputado do store a cada geração)**. Assim a
    justificativa não pode envelhecer em silêncio — se o dado mudar, o número
    que aparece ao lado do limite muda, e a discrepância fica visível na
    página em vez de ficar num documento que ninguém reabre (§4.43).
    """
    pm, px, ps = pisos["med"]
    fam = pisos["fam"]
    linhas = "".join(
        f'<tr><td>{_esc.escape(f[0])}</td><td>{f[1]}</td>'
        f'<td>{f[2]:.4f}</td><td>{f[3]:.4f}</td><td>{f[4]:.4f}</td></tr>'
        for f in fam[:12])
    return (
        f'<details class="crit"><summary><b>Por que estes limites</b> — '
        f'justificativa técnica das três pernas (âncoras medidas e '
        f'normativas)</summary>'
        f'<p>Um limite de erro só é honesto se estiver <b>acima da dispersão '
        f'do próprio experimento</b>. Abaixo dela, "reprovado" não mede o '
        f'modelo — mede o dado, e um modelo que passasse estaria perseguindo '
        f'ruído de digitalização e de espécime, que é a definição operacional '
        f'de <i>overfitting</i>. Os três valores abaixo saem daí.</p>'
        f'<table class="idx"><thead><tr><th>perna</th><th>limite</th>'
        f'<th>de onde vem</th></tr></thead><tbody>'
        f'<tr><td>res.máx</td><td><b>{META_MAX:.4g}</b></td><td>2× a margem de '
        f'decisão normativa, e <b>{100 * (META_MAX / px - 1) if px else 0:.0f}% '
        f'acima</b> do piso mediano medido ({px:.4f}). É a única perna que já '
        f'era ancorada antes de 2026-07-29.</td></tr>'
        f'<tr><td>MAE</td><td><b>{META_MAE:.4g}</b></td><td>= a <b>margem de '
        f'decisão das normas</b>: a ISO 16130:2015 põe a zona "boa" da retenção '
        f'de pré-carga em <b>85%</b> e a DIN 25201-4 aprova em <b>80%</b> ⇒ a '
        f'decisão de engenharia mora numa faixa de <b>0,05 em F/F₀</b>. Um erro '
        f'médio menor que ela não inverte veredicto de norma. Fica '
        f'{100 * (1 - META_MAE / pm) if pm else 0:.0f}% <b>abaixo</b> do piso '
        f'mediano ({pm:.4f}): escolha de ambição, com o custo na mesa '
        f'(<b>{n_imp_mae}</b> curvas de fontes cujo piso já viola o '
        f'limite).</td></tr>'
        f'<tr><td>σ_res</td><td><b>{META_SRES:.4g}</b></td><td>escolhido na '
        f'<b>mediana do piso de repetibilidade medido</b> — hoje esse piso é '
        f'<b>{ps:.4f}</b> ({len(fam)} famílias de réplica), '
        f'{"o limite está " + f"{100 * (1 - META_SRES / ps):.0f}% abaixo dele" if ps > META_SRES else "e o limite está " + f"{100 * (META_SRES / ps - 1):.0f}% acima dele" if ps else "sem piso medido"}. '
        f'É {META_SRES / _PISO_DIGITALIZACAO:.0f}× o piso de digitalização '
        f'declarado na literatura (±{_PISO_DIGITALIZACAO:.3f} em F/F₀, '
        f'Liu 2017: resolução de 5%/divisão) — logo mensurável. Custo: '
        f'<b>{n_imp_sd}</b> curvas de fontes com piso acima do limite.</td>'
        f'</tr></tbody></table>'
        f'<p class="sub2"><b>Nota de método (2026-07-29, tarde):</b> o piso é '
        f'medido por interpolação das réplicas na janela de x comum. A 1ª '
        f'versão exigia abscissas idênticas e enviesava o piso <b>para baixo</b> '
        f'— no Bauer fig6 sobrava 1 par de 15, e era o mais próximo: 0,0218 '
        f'contra 0,0959 com todos. Os limites acima foram escolhidos sobre a '
        f'medição enviesada (σ mediano 0,0241); com a correção o σ mediano é '
        f'{ps:.4f}. Quem decide se o limite acompanha é o professor — a página '
        f'permite testar ao vivo.</p>'
        f'<h4>1. O piso do próprio dado — medido, não estimado</h4>'
        f'<p>Uma <b>família</b> é o conjunto de curvas da MESMA fonte na MESMA '
        f'condição nominal (lida do <code>config_used</code>, não do nome do '
        f'arquivo). Para cada <b>par</b> da família comparo <b>dado contra '
        f'dado</b> na grade comum e meço as três réguas. Um modelo perfeito não '
        f'consegue erro menor que isto.</p>'
        f'<table class="idx"><thead><tr><th>família</th><th>n</th>'
        f'<th>MAE</th><th>res.máx</th><th>σ</th></tr></thead>'
        f'<tbody>{linhas}</tbody></table>'
        f'<p class="sub2">Mediana das {len(fam)} famílias: MAE <b>{pm:.4f}</b> '
        f'· res.máx <b>{px:.4f}</b> · σ <b>{ps:.4f}</b>. '
        f'<b>Repare na decomposição:</b> entre réplicas o σ é {ps:.3f} mas o '
        f'MAE é {pm:.3f} — a diferença é o <b>viés entre espécimes</b>, isto é '
        f'a dispersão de aperto. Vale <code>RMSE² = viés² + σ²</code> para o '
        f'experimento também, e por isso a perna de σ_res e a de MAE têm pisos '
        f'de natureza diferente: usar o mesmo raciocínio de tolerância para as '
        f'duas seria erro de dimensão.</p>'
        f'<h4>2. Âncoras normativas e de literatura</h4>'
        f'<table class="idx"><thead><tr><th>âncora</th><th>valor</th>'
        f'<th>procedência</th></tr></thead><tbody>'
        f'<tr><td>Fator de aperto α_A = F_max/F_min</td><td>1,0–1,1 '
        f'(tensionamento hidráulico) · <b>1,4–1,6 (torquímetro manual)</b></td>'
        f'<td>VDI 2230 Parte 1 (2015) §5.4.3</td></tr>'
        f'<tr><td>Dispersão de pré-carga pela variabilidade de µ</td>'
        f'<td><b>±50%</b> para o mesmo torque</td>'
        f'<td>LOOSENING_MECHANISMS_QUANTITATIVE.md</td></tr>'
        f'<tr><td>Dispersão de pré-carga em flange real</td><td>até <b>45%</b>; '
        f'±2,1% com 2 passes otimizados vs 25% em passe único</td>'
        f'<td>estudos de flange de torre eólica (Coria 2020 +)</td></tr>'
        f'<tr><td>A mesma dispersão vista no dado normalizado</td>'
        f'<td>réplicas partindo de <b>0,93–1,08</b> (±7,5% em F/F₀ antes do 1º '
        f'ciclo)</td><td>apparatus_notes/bauer2024_efa.md</td></tr>'
        f'<tr><td><b>Margem de decisão</b></td><td>ISO 16130:2015 <b>85%</b> · '
        f'DIN 25201-4 <b>80%</b> ⇒ faixa de <b>0,05</b></td>'
        f'<td>ISO 16130 / DIN 25201-4 (aviso implementado no analyzer V1)</td>'
        f'</tr>'
        f'<tr><td>Piso de digitalização</td><td><b>±0,005</b> em F/F₀ '
        f'(resolução 5%/divisão)</td>'
        f'<td>apparatus_notes/liu2017_triboint_axial.md</td></tr>'
        f'</tbody></table>'
        f'<h4>3. O que os limites tornam impossível (e por que isso é honesto '
        f'declarar)</h4>'
        f'<p><b>{n_imp_mae}</b> das {n} curvas pertencem a fontes cujo piso '
        f'medido de MAE já viola {META_MAE:.4g}, e <b>{n_imp_sd}</b> pertencem '
        f'a fontes cujo piso de σ já viola {META_SRES:.4g}. Nessas, <i>nem um '
        f'modelo perfeito passa</i> — são candidatas naturais a exceção '
        f'<b>por prova de piso</b>, não por julgamento. É o mesmo argumento das '
        f'exceções já assinadas ("a curva ideal já violaria a meta"), agora '
        f'contado em vez de alegado.</p>'
        f'<p class="sub2">Derivação completa, tabela integral das famílias e '
        f'contas de impacto de cada esquema alternativo: '
        f'<code>New_Theory/piso_repetibilidade_medido.md</code>. '
        f'{n_sd} das {n} curvas têm o campo <code>resid_std</code> — as demais '
        f'não podem ser julgadas na 3ª perna e saem do censo como '
        f'"não julgável", nunca como aprovadas.</p>'
        f'</details>')


def _fila_html(trio, pisos: dict) -> str:
    """FILA DE PRIORIDADE — o quanto o modelo está pior que o próprio dado.

    Item 2 das melhorias (2026-07-29). A prova de piso deu de graça a ordenação
    que a campanha precisava: para cada curva fora do tripé e **não** coberta por
    exceção, a razão `valor/piso` da perna mais violada diz o quanto o erro
    excede a dispersão que o experimento tem consigo mesmo.

    Por que a razão é melhor critério que o MAE absoluto: MAE puniria fontes
    ruidosas (onde nem o dado se reproduz) e absolveria fontes limpas com erro
    pequeno mas real. A razão normaliza pelo que é alcançável naquele rig —
    `yang2021_fig2_typical` a 11,5× é um alvo muito mais legítimo que uma curva
    de MAE maior numa fonte cujo piso é alto.

    Quem não tem piso medido não entra na ordenação (e o painel diz isso em vez
    de ordená-las por um número que não existe)."""
    linhas, sem_piso = [], []
    for t in trio:
        mae, mx, _rmse, _b, cid, sd, src = t
        if (mx <= META_MAX and mae <= META_MAE
                and sd is not None and sd <= META_SRES):
            continue                       # dentro do tripé
        if cid in _EXCECOES:
            continue                       # exceção assinada: fora da fila
        p = pisos["por_fonte"].get(src)
        viol = []
        if mx > META_MAX:
            viol.append(("res.máx", mx, p[1] if p else None))
        if mae > META_MAE:
            viol.append(("MAE", mae, p[0] if p else None))
        if sd is None or sd > META_SRES:
            viol.append(("σ_res", sd, p[2] if p else None))
        com = [(n, v, f) for n, v, f in viol
               if f and v is not None and f > 0]
        if not com:
            sem_piso.append((cid, src, viol))
            continue
        n, v, f = max(com, key=lambda z: z[1] / z[2])
        linhas.append((v / f, cid, src, n, v, f))
    linhas.sort(reverse=True)
    if not linhas and not sem_piso:
        return ""
    corpo = "".join(
        f'<tr><td><a href="reports/{_esc.escape(cid)}.html">'
        f'{_esc.escape(cid)}</a></td><td>{_esc.escape(src)}</td>'
        f'<td>{n}</td><td>{v:.4f}</td><td>{f:.4f}</td>'
        f'<td class="{"warn" if r >= 2 else ""}">{r:.1f}×</td></tr>'
        for r, cid, src, n, v, f in linhas)
    sp = ""
    if sem_piso:
        sp = (f'<p class="sub2"><b>{len(sem_piso)} curva(s) sem piso medido</b> '
              f'não entram na ordenação — a fonte não tem réplica em condição '
              f'repetida, então não há denominador. Elas não são "melhores" nem '
              f'"piores": são <b>não ordenáveis</b> até alguém medir o piso '
              f'(duas corridas na mesma condição bastam). '
              + " · ".join(f'<code>{_esc.escape(c)}</code>'
                           for c, _s, _v in sem_piso[:8])
              + ("…" if len(sem_piso) > 8 else "") + '</p>')
    pior = linhas[0] if linhas else None
    return (
        f'<h3>Fila de prioridade — quanto o modelo está pior que o dado</h3>'
        f'<p class="sub2">As <b>{len(linhas)}</b> curvas fora do tripé que '
        f'<b>não</b> são exceção assinada, ordenadas pela razão '
        f'<code>valor/piso</code> da perna mais violada. O piso é a '
        f'repetibilidade MEDIDA da fonte (dado contra dado): razão 1,0 significa '
        f'"o modelo erra tanto quanto dois ensaios idênticos discordam"; '
        f'{f"o topo da fila está em <b>{pior[0]:.1f}×</b> (<code>{_esc.escape(pior[1])}</code>, {pior[3]})" if pior else ""}. '
        f'Esta razão é melhor critério de prioridade que o MAE absoluto, que '
        f'puniria fonte ruidosa e absolveria fonte limpa com erro real.</p>'
        f'<details class="crit"><summary>ver a fila ({len(linhas)} curvas, '
        f'da pior para a melhor)</summary>'
        f'<div class="ovx"><table class="idx"><thead><tr><th>curva</th>'
        f'<th>fonte</th><th>perna pior</th><th>valor</th><th>piso</th>'
        f'<th>razão</th></tr></thead><tbody>{corpo}</tbody></table></div>'
        f'{sp}</details>')


def _controles_html(mae: float, mx: float, sd: float) -> str:
    """Controles AO VIVO dos três limites (pedido: *"melhorar esses gráficos e
    sua interatividade"*). Enhancement progressivo: o SVG que o Python emitiu já
    está correto nos valores padrão, então **sem JS a página continua íntegra e
    imprimível** — os controles só recolorem/reprojetam o que já está lá."""
    return (
        f'<div class="ctl" id="ctl-lim">'
        f'<span class="ctl-t">limites ao vivo</span>'
        f'<label>res.máx <input type="range" id="in-mx" min="0.02" max="0.30" '
        f'step="0.005" value="{mx:.4g}"><output id="ou-mx">{mx:.4g}</output>'
        f'</label>'
        f'<label>MAE <input type="range" id="in-mae" min="0.01" max="0.20" '
        f'step="0.005" value="{mae:.4g}"><output id="ou-mae">{mae:.4g}</output>'
        f'</label>'
        f'<label>σ_res <input type="range" id="in-sd" min="0.002" max="0.06" '
        f'step="0.001" value="{sd:.4g}"><output id="ou-sd">{sd:.4g}</output>'
        f'</label>'
        f'<label>profundidade do 3D '
        f'<select id="in-z"><option value="d">σ_res (3ª perna)</option>'
        f'<option value="r">RMSE</option>'
        f'<option value="b">|viés|</option></select></label>'
        f'<label>escala <select id="in-esc">'
        f'<option value="abs">absoluta (F/F₀)</option>'
        f'<option value="lim">×limite, escala √</option></select></label>'
        f'<label>cor <select id="in-cor">'
        f'<option value="grad">distância à origem (gradiente)</option>'
        f'<option value="perna">perna que manda</option>'
        f'<option value="tripe">passa/não passa</option></select></label>'
        f'<label title="ocultar/mostrar as exceções assinadas (losango) no 3D; '
        f'a chave declara quantas estão ocultas"'
        f'><input type="checkbox" id="in-exc" checked> ◆ exceções</label>'
        f'<label title="ocultar/mostrar as declaradas (quadrado) no 3D">'
        f'<input type="checkbox" id="in-decl" checked> ■ declaradas</label>'
        f'<button type="button" id="bt-reset">restaurar padrão</button>'
        f'<span class="ctl-h">arraste dentro do 3D para girar (ou as setas, com '
        f'o gráfico em foco) · passe o mouse num ponto para lê-lo abaixo · '
        f'clique abre o report do caso · <b>escala ×limite</b> põe as três '
        f'pernas na mesma unidade e descomprime o canto denso</span></div>'
        # Leitor de foco: com 202 pontos e vizinho mediano a 1,5 px, o `<title>`
        # nativo (≈1 s parado) não resolve uma curva. Nasce com o texto de
        # instrução, que o JS guarda como estado "vazio" e restaura no mouseout.
        f'<div class="s3i" id="s3-info">passe o mouse (ou o foco) sobre um '
        f'ponto do gráfico 3D para ver a curva, as três réguas em múltiplos do '
        f'limite e qual perna manda.</div>')


def _payload_js(trio, pisos=None) -> str:
    """Dados por curva + a lógica interativa. O payload é compacto de propósito
    (chaves de 1 letra, 4 casas): 200 curvas × 6 números cabem em ~20 kB, e o
    arquivo continua abrindo em `file://` sem servidor.

    `pf` = piso da fonte (D1). O JS usa `max(L.sd, pf)` como limite efetivo da
    3ª perna — assim o slider continua sendo o limite GLOBAL (subir afrouxa
    tudo), e o piso por fonte só age como mínimo. Emitido apenas com
    `_SRES_POR_FONTE` ligado e piso acima do global; senão fica fora do payload
    e o JS se comporta exatamente como antes."""
    dat = []
    for t in trio:
        d = {"c": t[4], "s": t[6],
             "a": round(t[0], 4), "x": round(t[1], 4),
             "d": None if t[5] is None else round(t[5], 5),
             "r": None if t[2] is None else round(t[2], 4),
             "b": None if t[3] is None else round(abs(t[3]), 4)}
        # `e` = ESTATUTO, do MESMO helper que o SVG do Python usa: é o que
        # impede a forma do marcador de divergir entre estático e interativo.
        # Só emitido quando existe (a maioria é "" — payload continua enxuto).
        _e = estatuto_da_curva(t[4])
        if _e:
            d["e"] = _e
        if _SRES_POR_FONTE and pisos:
            lim = limite_sres(t[6], pisos)
            if lim > META_SRES:
                d["pf"] = round(lim, 5)
        dat.append(d)
    payload = json.dumps(dat, ensure_ascii=False, separators=(",", ":"))
    defaults = json.dumps({"mae": META_MAE, "mx": META_MAX, "sd": META_SRES},
                          separators=(",", ":"))
    return ('<script>window.__BAS3__=' + payload
            + ';window.__BAS3DEF__=' + defaults + ';</script>'
            + '<script>' + _JS_PAINEL + '</script>')


def _fontes_fechadas_html(porf: Dict[str, List[int]]) -> str:
    """As fontes que fecharam 100 %, NOMEADAS.

    O gráfico de barras mede "curvas fora", então quem fechou tem barra de
    comprimento zero e **desaparece do desenho**. O leitor via um contador
    ("6 de 28") e nenhuma pista de quais — mas essa é metade da informação útil:
    saber que o LIU_2017_AXIAL fecha 9/9 enquanto o LU_2024 falha 10/10 é o que
    separa "problema da fonte" de "problema do modelo". Ausência de barra não é
    ausência de fato."""
    fechadas = sorted((s, v[1]) for s, v in porf.items() if not v[0])
    if not fechadas:
        return ('<p class="sub2">Nenhuma fonte fechou 100 % — todas têm ao menos '
                'uma curva fora do tripé.</p>')
    itens = " · ".join(
        f'<span class="bdg ok">{_esc.escape(s)} {n}/{n}</span>'
        for s, n in fechadas)
    return (f'<p class="sub2"><b>Fecharam 100 % ({len(fechadas)} de '
            f'{len(porf)}) — sem barra porque a barra mede o que falta:</b><br>'
            f'{itens}</p>')


def _conteudo_preditivo_html(comp: List[CaseRecord],
                             results: Dict[str, Optional[CaseResult]],
                             pisos: dict) -> str:
    """CONTEÚDO PREDITIVO por fonte — o modelo separa as condições que o
    experimento varreu? (item L, prereg `2026-08-14-item-L-...`, assinado.)

    ⚠️ **Isto NÃO é uma 4ª perna e NÃO é meta.** O tripé mede o ERRO; isto mede
    outra coisa: se o modelo REAGE ao que o ensaio mudou. Uma curva entra no
    censo quando o erro cabe na tolerância — e o efeito varrido pode ser MENOR
    que essa tolerância. Nesse caso o modelo acerta o nível e erra a física
    inteira do ensaio, sem que nenhuma métrica reclame.

    Caso que motivou (medido 2026-08-14): o `LIU_2020_WEAR` varria a amplitude
    transversal 4× e o modelo devolvia **0,9650 nas quatro** — 8/9 no tripé com
    4 predições distintas para 9 condições. O canal de flanco, adotado em
    2026-08-15, levou o espalhamento de 0,0000 a 0,0777 (dado 0,1569).

    MÉTODO — par a par DENTRO da fonte, na janela comum, só entre curvas que
    PASSAM o tripé:

        d_dado = média |dado_i − dado_j| ;  d_mod = média |modelo_i − modelo_j|
        razão  = d_mod / d_dado    (≈0 ⇒ o modelo não distingue as condições)

    ⚠️ DUAS ARMADILHAS, cada uma já medida como erro:

    1. O par só entra se `d_dado` exceder o piso de RÉPLICA **DAQUELA FONTE**,
       nunca o global. Com o piso global o `CACCESE_2009` aparece "cego" quando
       o que ocorre é que o scatter réplica-réplica dele (0,0549) EXCEDE o
       efeito de geometria (0,0101–0,0449) — o dado não pode exigir a
       separação. Com o piso certo ele é dos melhores (≈1,04).
    2. Publica-se a MEDIANA por fonte, nunca a CONTAGEM de pares cegos: o
       número de pares cresce com n², então contagem pune fonte grande. O
       `LIU_2022_RETIGHT` lidera em contagem (17) e é das melhores normalizado
       (≈0,85 sobre ~100 pares).
    """
    porf: dict = {}
    for r in comp:
        res = results.get(r.case_id)
        if not (res and res.ok):
            continue
        sd = sres_para_censo(res)
        if sd is None or res.mae is None or res.maxerr is None:
            continue
        if not (res.mae <= META_MAE and res.maxerr <= META_MAX
                and sd <= limite_sres(r.source, pisos)):
            continue                      # só curvas que PASSAM
        x = getattr(res, "metric_x", None)
        d = getattr(res, "metric_data", None)
        p = getattr(res, "metric_pred", None)
        if not (x and d and p and len(x) >= 4):
            continue
        porf.setdefault(r.source, []).append(
            (list(map(float, x)), list(map(float, d)), list(map(float, p))))

    pf_map = (pisos or {}).get("por_fonte") or {}
    linhas = []
    for src, curvas in porf.items():
        pf = pf_map.get(src)
        # ⚠️ `_PISO_DIGITALIZACAO` JA' EXISTE no modulo (0,005, Liu 2017). A 1a
        # versao desta funcao inventou um `_PISO_DIGIT` — constante nova para um
        # valor que o modulo ja carregava, com o risco classico de divergirem.
        piso = max(_PISO_DIGITALIZACAO, float(pf[0]) if pf else 0.0)
        razoes = []
        for i in range(len(curvas)):
            for j in range(i + 1, len(curvas)):
                (xa, da, pa), (xb, db, pb) = curvas[i], curvas[j]
                lo, hi = max(min(xa), min(xb)), min(max(xa), max(xb))
                if hi <= lo:
                    continue
                # numpy ja' esta importado no modulo — `np.interp` em vez de
                # escrever interpolacao a mao (mesma convencao das sondas que
                # mediram estes numeros).
                g = np.linspace(lo, hi, 60)
                dd = float(np.mean(np.abs(np.interp(g, xa, da)
                                          - np.interp(g, xb, db))))
                if dd < piso:            # o dado não separa: não acusa
                    continue
                dm = float(np.mean(np.abs(np.interp(g, xa, pa)
                                          - np.interp(g, xb, pb))))
                razoes.append(dm / dd)
        if razoes:
            razoes.sort()
            n = len(razoes)
            med = (razoes[n // 2] if n % 2
                   else 0.5 * (razoes[n // 2 - 1] + razoes[n // 2]))
            linhas.append((med, src, n, piso))
    if not linhas:
        return ""
    linhas.sort()
    todas = sorted(l[0] for l in linhas)
    m = len(todas)
    medg = (todas[m // 2] if m % 2
            else 0.5 * (todas[m // 2 - 1] + todas[m // 2]))
    tr = "".join(
        f'<tr><td>{_esc.escape(s)}</td>'
        f'<td class="num"><b>{r:.3f}</b></td>'
        f'<td class="num">{n}</td><td class="num">{p:.4f}</td>'
        f'<td>{"⚠️ tripé cheio e cego" if (r < 0.20) else ("fraco" if r < 0.40 else "")}</td></tr>'
        for r, s, n, p in linhas)
    return (
        f'<h3>Conteúdo preditivo — o modelo separa as condições?</h3>'
        f'<p class="sub2"><b>Não é uma 4ª perna e não é meta.</b> O tripé mede o '
        f'<b>erro</b>; isto mede se o modelo <b>reage</b> ao que o ensaio mudou. '
        f'Uma curva entra no censo quando o erro cabe na tolerância — e o efeito '
        f'varrido pode ser <b>menor que a tolerância</b>, caso em que o modelo '
        f'acerta o nível e erra a física do ensaio sem que nenhuma métrica '
        f'reclame. Forçar esta razão a 1 seria pedir que o modelo reproduzisse o '
        f'<i>scatter</i>: ela é leitura, como o RMSE na cunha.</p>'
        f'<p class="sub2">Par a par dentro da fonte, na janela comum, só entre '
        f'curvas que <b>passam</b>; o par entra apenas se o dado as separar acima '
        f'do <b>piso de réplica da própria fonte</b> (coluna <i>piso</i>) — com o '
        f'piso global uma fonte ruidosa apareceria "cega" quando é o dado que não '
        f'distingue. <b>Mediana das medianas: {medg:.3f}</b> em {len(linhas)} '
        f'fontes.</p>'
        f'<table class="tbl"><thead><tr><th>fonte</th>'
        f'<th class="num">razão d_mod/d_dado</th><th class="num">pares</th>'
        f'<th class="num">piso</th><th>leitura</th></tr></thead>'
        f'<tbody>{tr}</tbody></table>')


def _erro_section(comp: List[CaseRecord],
                  results: Dict[str, Optional[CaseResult]]) -> str:
    """"Onde está o erro" — três leituras do MESMO conjunto, na ordem da
    pergunta que esta página existe para responder: (1) que fontes faltam,
    (2) quão longe da meta está o erro, (3) qual das duas métricas é o
    gargalo. Tudo SVG estático: imprime, funciona sem JS e não depende do
    renderer de séries temporais (cujo eixo x é de ciclos, inteiro)."""
    dados = []
    # TRÊS PERNAS desde 2026-07-29 (res.máx · MAE · σ_res). `rmse` e `resid_std`
    # já vinham no store — o painel só não os desenhava. `trio` anda em paralelo
    # a `dados` de propósito: os laços que já liam 3-tuplas continuam intactos.
    trio = []          # (mae, maxerr, rmse, viés, rótulo, σ_res, fonte)
    for r in comp:
        res = results.get(r.case_id)
        if res and res.ok and res.mae is not None and res.maxerr is not None:
            dados.append((r.source, float(res.mae), float(res.maxerr)))
            # sigma via `sres_para_censo` (regra n<6 assinada 2026-08-01):
            # None = nao-julgavel, e todos os laços deste painel ja tratam
            # t[5] is None como "nao passa" (convencao do sigma ausente).
            _sd = sres_para_censo(res)
            trio.append((float(res.mae), float(res.maxerr),
                         None if res.rmse is None else float(res.rmse),
                         _bias_of(res), r.case_id,
                         None if _sd is None else float(_sd), r.source))
    if not dados:
        return ""
    n = len(dados)
    # piso de repetibilidade RECOMPUTADO do store (não constante: se o dado
    # mudar, a justificativa dos limites tem de mudar com ele)
    pisos = _pisos_medidos([(r.source, results[r.case_id]) for r in comp
                            if results.get(r.case_id)])
    piso_sd = pisos["med"][2]   # os outros dois vivem em _criterio_html
    # A FAIXA dos pisos por fonte. Dizer "o piso medido é 0,028" no singular —
    # como a página dizia — faz o leitor concluir que existe UM piso do conjunto.
    # Não existe: medido em 2026-07-29 sobre 22 fontes com réplica, ele vai de
    # **0,00094** (GRZEJDA_2026) a **0,22139** (JCSR_2023) = **236×**, isto é o
    # extremo superior é 8,9× o limite global e o inferior 0,04× dele. E essa
    # conclusão errada é exatamente o argumento a favor de um limite por fonte,
    # invertido. Calculado AQUI (e não junto do histograma) porque o texto de
    # explicação, que é o que se lê sem passar o mouse, precisa dele também.
    _sp = sorted(v[2] for v in pisos["por_fonte"].values())
    _faixa = (f" · varia {_sp[0]:.3f}–{_sp[-1]:.3f} por fonte"
              if len(_sp) > 1 else "")

    # D1 (adotado 2026-07-30): o limite EFETIVO da 3ª perna é por fonte —
    # `max(META_SRES, piso medido)`. Com a flag desligada `limite_sres` devolve
    # o global e TODA esta fiação é inerte (bit-idêntica). O censo, as contagens
    # "só uma perna", a perna-que-manda, as cores do 3D e o payload do JS têm de
    # usar o MESMO limite — metade da página numa régua e metade na outra foi
    # exatamente o defeito que o report por caso teve em 2026-07-29.
    def _lim(src: str) -> float:
        return limite_sres(src, pisos)

    def _ok3(t):
        return (t[1] <= META_MAX and t[0] <= META_MAE
                and t[5] is not None and t[5] <= _lim(t[6]))

    n_ok = sum(1 for t in trio if _ok3(t))
    n_so_mae = sum(1 for t in trio if t[0] > META_MAE
                   and t[1] <= META_MAX
                   and (t[5] is None or t[5] <= _lim(t[6])))
    n_so_mx = sum(1 for t in trio if t[1] > META_MAX and t[0] <= META_MAE
                  and (t[5] is None or t[5] <= _lim(t[6])))
    n_so_sd = sum(1 for t in trio if t[5] is not None and t[5] > _lim(t[6])
                  and t[0] <= META_MAE and t[1] <= META_MAX)
    n_ambos = n - n_ok - n_so_mae - n_so_mx - n_so_sd
    porf: Dict[str, List[int]] = {}
    for t in trio:
        d = porf.setdefault(t[6], [0, 0])
        d[1] += 1
        if not _ok3(t):
            d[0] += 1
    rows = sorted(((s, v[0], v[1]) for s, v in porf.items() if v[0]),
                  key=lambda z: (-z[1], z[0]))
    n_fontes_ok = sum(1 for v in porf.values() if not v[0])
    # a leitura que o número sozinho não dá: qual perna manda
    _mand = max((n_so_mae, "o MAE"), (n_so_mx, "o resíduo máximo"),
                (n_so_sd, "o σ_res"))
    # DUAS contagens diferentes, e confundi-las dá a resposta errada:
    #  · "viola SÓ esta perna" (abaixo) = onde um conserto de uma perna fecha a
    #    curva inteira;
    #  · "esta perna MANDA" (`_manda`, o argmax dos múltiplos) = quem domina a
    #    distância à origem, mesmo quando outras também violam. É esta que
    #    responde "onde o esforço rende", porque é a que segura o veredito.
    _md: Dict[str, int] = {}
    for t in trio:
        p = _perna_manda(t[0], t[1], t[5], META_MAE, META_MAX, _lim(t[6]))
        if p is not None:
            _md[p] = _md.get(p, 0) + 1
    _NMP = {"mae": "o MAE", "mx": "o res.máx", "sd": "o σ_res"}
    _dom = max(_md.items(), key=lambda kv: kv[1]) if _md else None
    manda_txt = ""
    if _dom:
        manda_txt = (
            f' <b>Quem MANDA</b> (o maior múltiplo do limite, isto é quem segura '
            f'o veredito): '
            + " · ".join(f"{v} {_NMP[k]}" for k, v in
                         sorted(_md.items(), key=lambda kv: -kv[1]))
            + f' — <b>{_NMP[_dom[0]]}</b> domina '
              f'{100.0 * _dom[1] / max(sum(_md.values()), 1):.0f}% das '
              f'{sum(_md.values())} fora.')
    veredito = (f'Violam <b>só</b> uma perna: {n_so_mae} o MAE · {n_so_mx} o '
                f'res.máx · {n_so_sd} o σ_res; {n_ambos} violam mais de uma. '
                f'A perna que sozinha reprova mais é <b>{_mand[1]}</b> '
                f'({_mand[0]} curvas).{manda_txt}')
    mxs_ = [b for _, _, b in dados]
    mas_ = [a for _, a, _ in dados]
    # --- as réguas auxiliares: RMSE (leitura) e a decomposição dele
    rms_ = [t[2] for t in trio if t[2] is not None]
    sds_ = [t[5] for t in trio if t[5] is not None]
    # 5º elemento = limite EFETIVO da 3ª perna daquela curva (D1); com a flag
    # desligada é META_SRES para todas e o desenho sai idêntico ao de antes
    pts3 = [(t[0], t[1], t[5], t[4], _lim(t[6])) for t in trio
            if t[5] is not None]
    share_ = [min(abs(t[3]) / t[2], 1.0) for t in trio
              if t[2] is not None and t[2] > 1e-12 and t[3] is not None]
    n_rms = len(rms_)
    rms_med = sorted(rms_)[len(rms_) // 2] if rms_ else 0.0
    # nenhuma norma-p do mesmo vetor escapa do sanduíche: conferido, não suposto
    n_squeeze = sum(1 for t in trio if t[2] is not None
                    and not (t[0] - 1e-12 <= t[2] <= t[1] + 1e-12))
    tri_ok = [t for t in trio if _ok3(t)]
    # curvas que o limite torna IMPOSSÍVEIS: a fonte tem piso medido acima dele
    n_imposs_mae = sum(1 for t in trio
                       if pisos["por_fonte"].get(t[6], (0, 0, 0))[0] > META_MAE)
    n_imposs_sd = sum(1 for t in trio
                      if pisos["por_fonte"].get(t[6], (0, 0, 0))[2] > META_SRES)
    n_uni = sum(1 for t in tri_ok if t[2] and t[3] is not None
                and t[0] > 1e-12 and abs(t[3]) / t[0] > 0.99)
    n_osc = sum(1 for t in tri_ok if t[2] and t[3] is not None
                and t[0] > 1e-12 and abs(t[3]) / t[0] <= 0.50)
    # p95 do |viés| entre as aprovadas. O índice tem de sair do TAMANHO DA
    # LISTA, não de `len(tri_ok)`: registros sem os vetores da métrica (store
    # antigo, casos sintéticos dos testes) não entram, a lista fica menor e
    # indexar pelo outro tamanho estoura — foi o IndexError de 2026-07-29.
    _bs = sorted(abs(t[3]) for t in tri_ok if t[3] is not None)
    bias_p95 = _bs[int(0.95 * (len(_bs) - 1))] if _bs else 0.0
    prox = sum(1 for v in mxs_ if META < v <= 0.15)
    longe = sum(1 for v in mxs_ if v > 0.30)
    top3 = sum(v for _, v, _ in rows[:3])
    top3n = ", ".join(s for s, _, _ in rows[:3])
    pior = max(mxs_)
    ex_barras = _explica(
        "Onde está o trabalho que falta: quais artigos ainda têm curva fora "
        "da meta, e quantas.",
        [("uma barra", "uma <b>fonte</b> — o artigo/bancada de onde as curvas "
                       "foram digitalizadas (chave do registry)"),
         ("comprimento", "número de curvas daquela fonte <b>fora do tripé</b>"),
         ("rótulo à direita", "<code>fora/total</code> — quantas violam de "
                              "quantas curvas comparáveis a fonte tem"),
         ("ordem", "decrescente pelo número de curvas fora"),
         ("ausência", f"fontes que fecharam 100% não aparecem "
                      f"({n_fontes_ok} hoje)")],
        "A barra do topo é onde está a maior massa de trabalho restante. "
        "Compare o comprimento com o rótulo: uma fonte com 10/10 está "
        "inteiramente fora (problema sistemático da fonte), enquanto 2/14 "
        "são casos isolados.",
        f"{len(rows)} fontes têm ao menos uma curva fora e {n_fontes_ok} de "
        f"{len(porf)} fecharam 100%. As três maiores ({top3n}) somam "
        f"<b>{top3}</b> das {n - n_ok} curvas fora — "
        f"{100.0 * top3 / max(n - n_ok, 1):.0f}% do que falta está em 3 "
        f"fontes, o que favorece atacar por fonte e não curva a curva.")
    ex_hist = _explica(
        "Quão longe da meta está cada curva — não só quantas falham, mas por "
        "quanto. Os três primeiros painéis são as três PERNAS do tripé; o "
        "quarto é diagnóstico, não porta.",
        [("eixo x", f"faixa de erro, em passos próprios de cada régua ({_UNI}); "
                    f"no 4º painel é fração adimensional"),
         ("eixo y", "número de curvas na faixa (escrito acima da barra)"),
         ("MAE", f"erro <b>médio</b> absoluto ao longo da curva — limite "
                 f"<b>{META_MAE:.4g}</b>, que é a margem de decisão das normas "
                 f"(ISO 16130 85% vs DIN 25201-4 80%)"),
         ("res.máx", f"maior desvio <b>pontual</b> |modelo − dado| — limite "
                     f"<b>{META_MAX:.4g}</b>, 2× a margem normativa"),
         ("σ_res", f"desvio-padrão do resíduo <b>assinado</b>: mede se o erro "
                   f"<b>oscila em torno</b> do dado ou vagueia — limite "
                   f"<b>{META_SRES:.4g}</b>, a mediana do piso de "
                   f"repetibilidade medido ({piso_sd:.4f})"),
         ("|viés|/RMSE", "quanto do erro é <b>sistemático</b>: 0 = o modelo "
                         "cruza o dado e oscila em torno dele; 1 = o resíduo "
                         "<b>nunca troca de sinal</b>. Vem da identidade exata "
                         "<code>RMSE² = viés² + σ_res²</code>"),
         ("verde / vermelho", "faixa inteiramente abaixo do limite / acima "
                              "dele — no 4º painel o vermelho marca a faixa "
                              "unilateral, que <b>não é reprovação</b>: não há "
                              "limite declarado para viés"),
         ("vermelho <b>pálido</b>", "a faixa que o limite <b>corta pelo meio</b> "
                                    "— parte das curvas dela passa e parte não. "
                                    "Pintá-la de verde faria somar aprovadas "
                                    "que não existem; o número exato está no "
                                    "contador do topo, não no histograma"),
         ("linha tracejada vermelha", "o limite daquela perna (ausente no 4º "
                                      "painel de propósito)"),
         ("linha pontilhada cinza", f"só no painel do σ_res: a <b>MEDIANA</b> do "
                                    f"piso de repetibilidade medido "
                                    f"(<b>{piso_sd:.4f}</b> — passe o mouse "
                                    f"nela). Abaixo dele o critério pediria "
                                    f"fidelidade que o experimento não tem "
                                    f"consigo mesmo; é por isso que o limite "
                                    f"desta perna foi posto <i>nele</i>, e não "
                                    f"num número redondo. <b>Uma linha só engana "
                                    f"se lida como “o” piso:</b> ele é medido "
                                    f"<b>por fonte</b> e"
                                    + (f" vai de <b>{_sp[0]:.4f}</b> a "
                                       f"<b>{_sp[-1]:.4f}</b> (×"
                                       f"{_sp[-1]/max(_sp[0], 1e-9):.0f} entre a "
                                       f"fonte mais quieta e a mais ruidosa), "
                                       f"logo há fontes cujo piso é "
                                       f"{_sp[-1]/META_SRES:.1f}× o limite "
                                       f"global — nelas, reprovar mede o "
                                       f"experimento, não o modelo"
                                       if len(_sp) > 1 else
                                       " varia entre elas")),
         ("última barra", "transbordo do eixo")],
        "Some as barras vermelhas: é o total fora do limite naquela perna. "
        "A barra logo à direita da linha tracejada são as curvas <i>a um "
        "passo</i> — normalmente o alvo de melhor retorno. Barras no fim da "
        "cauda são casos estruturais, não de ajuste fino. No painel do viés a "
        "leitura é outra: massa à <b>esquerda</b> = erro que oscila em torno "
        "do dado (o que se quer); massa à <b>direita</b> = erro deslocado, que "
        "pode ser pequeno e ainda assim estar sempre do mesmo lado.",
        f"Violam o limite: <b>{sum(1 for v in mas_ if v > META_MAE)}</b> no "
        f"MAE · <b>{sum(1 for v in mxs_ if v > META_MAX)}</b> no res.máx · "
        f"<b>{sum(1 for v in sds_ if v > META_SRES)}</b> no σ_res (de "
        f"{len(sds_)} com o campo). Das que violam o pico, <b>{prox}</b> estão "
        f"na primeira faixa acima do limite e <b>{longe}</b> passam de 0.30; o "
        f"pior chega a {pior:.2f}. <b>Réguas auxiliares:</b> RMSE mediano "
        f"{rms_med:.4f} em {n_rms} curvas — ele NÃO é perna, porque "
        f"<code>MAE &le; RMSE &le; res.máx</code> vale sempre "
        f"(<b>{n_squeeze}</b> violações medidas) e um limite nele seria "
        f"redundante. A informação que ele carrega está no 4º painel: "
        f"<b>{n_uni}</b> das {len(tri_ok)} aprovadas têm resíduo que nunca "
        f"troca de sinal contra <b>{n_osc}</b> que oscilam de fato "
        f"(|viés| &le; metade do MAE); p95 do |viés| = {bias_p95:.4f}.")
    ex_disp = _explica(
        "Qual das três pernas é o gargalo — a pergunta que decide onde gastar "
        "esforço. Em 3D desde 2026-07-29, com a 3ª perna no eixo de "
        "profundidade.",
        [("um ponto", "uma curva de validação (passe o mouse para nome e as "
                      "três réguas; clique para abrir o report do caso)"),
         ("eixo x", f"MAE da curva ({_UNI})"),
         ("eixo y", "resíduo máximo da curva, mesma unidade"),
         ("eixo de profundidade", "a 3ª perna (σ_res por padrão; o seletor "
                                  "troca por RMSE ou |viés|) — cresce para "
                                  "cima e para a direita"),
         ("caixa tracejada", f"o tripé é um <b>volume</b>: MAE {META_MAE:.4g} × "
                             f"res.máx {META_MAX:.4g} × σ_res "
                             f"{META_SRES:.4g}. Arestas <b>desiguais</b>, "
                             f"porque as três pernas não têm o mesmo valor"),
         ("linhas de grade", "cada linha é <b>um limite</b> daquela perna (não "
                             "um quarto do teto): a 1ª coincide com a aresta da "
                             "caixa, então dá para ler <i>“entre a 3ª e a 4ª "
                             "linha ⇒ 3–4× o limite”</i> contando, sem conta "
                             "mental. O tique do limite sai na cor do eixo"),
         ("cor do ponto (padrão)", "<b>gradiente da distância à origem</b> — a "
                                   "origem é o modelo perfeito. A distância é o "
                                   "<b>maior múltiplo de limite</b> estourado, "
                                   "<code>d = max(MAE/0,05 · res.máx/0,10 · "
                                   "σ_res/0,025)</code>, e a rampa vai de verde "
                                   "em 0 a vermelho em 3×. O âmbar cai em "
                                   "<b>d = 1</b>, que é a <b>superfície da "
                                   "caixa</b>: como a meta é uma conjunção "
                                   "(<i>E</i> lógico), ela É a condição "
                                   "<code>d ≤ 1</code> — logo a cor e a caixa "
                                   "nunca se contradizem. Com distância "
                                   "euclidiana isso falharia: (1,5 · 0,1 · "
                                   "0,1)× tem norma 0,87 e ainda assim reprova "
                                   "no MAE"),
         ("cor do ponto (outros modos)", "o seletor troca por <b>perna que "
                                         "manda</b> — a cor do eixo cuja "
                                         "violação é maior em múltiplos "
                                         "(<span style='color:var(--di)'>■ "
                                         "MAE</span> · <span "
                                         "style='color:var(--warn)'>■ "
                                         "res.máx</span> · <span "
                                         "style='color:var(--accent)'>■ "
                                         "σ_res</span>, verde = passa) — ou "
                                         "pelo <b>passa/não passa</b> binário. "
                                         "Gradiente e perna são o mesmo número "
                                         "partido em dois: o <b>máximo</b> "
                                         "(quão longe) e o <b>argmáximo</b> "
                                         "(por onde)"),
         ("triângulo ▲", "curva <b>recortada</b> no teto do eixo: a posição não "
                         "é o valor dela (o valor real está no tooltip e no "
                         "leitor). Um círculo em cima da borda afirmaria um "
                         "número que não é o dado"),
         ("ponto cinza e a haste", "a <b>sombra</b> da curva no plano da frente "
                                   "(3ª perna = 0): é exatamente o gráfico 2D "
                                   "que este substituiu"),
         ("teto de cada eixo", "próprio de cada régua — o σ_res vive em "
                               "0–0.10 e o res.máx em 0–0.60; um teto comum "
                               "esconderia a 3ª perna dentro de 2% do eixo"),
         ("escala ×limite", "reprojeta os três eixos em <b>múltiplos do próprio "
                            "limite</b>, com escala <b>√</b> e teto comum de "
                            "9×. Duas consequências: as pernas passam a ter a "
                            "MESMA unidade (a caixa vira um <b>cubo</b>, e "
                            "distância visual igual = severidade igual) e o "
                            "canto denso descomprime — as 104 aprovadas saem de "
                            "<b>2,68 %</b> para <b>9,81 %</b> da área "
                            "(3,66× medido no render), sem recortar nenhuma "
                            "curva"),
         ("controles", "os três limites são <b>ajustáveis ao vivo</b>; arraste "
                       "no gráfico (ou use as setas, com ele em foco) para "
                       "girar; o <b>leitor abaixo do gráfico</b> mostra a curva "
                       "sob o cursor com as três réguas em múltiplos do "
                       "limite")],
        "Duas leituras. (1) A <b>sombra</b> responde a pergunta antiga: acima "
        "e à esquerda = passa no MAE e falha no pico. (2) A <b>altura da "
        "haste</b> é a perna nova: haste curta = o resíduo é quase constante "
        "(erro de NÍVEL, o modelo mora de um lado); haste longa = o resíduo "
        "varia muito ao longo da curva (erro de FORMA). As duas doenças pedem "
        "correções diferentes, e é por isso que a 3ª perna não é redundante "
        "com as outras duas.",
        f"{veredito} No tripé <b>{n_ok}</b> de {n} "
        f"({100.0 * n_ok / max(n, 1):.0f}%).")
    # As chamadas ficam FORA do return de propósito: uma expressão de f-string
    # não pode ser quebrada em duas literais adjacentes (SyntaxError, e o
    # arquivo só falha no import).
    h_mae = _svg_hist(mas_, "MAE (1ª perna)", step=0.025, nb=12,
                      meta=META_MAE, key="mae")
    h_mx = _svg_hist(mxs_, "resíduo máximo (2ª perna)", step=0.05, nb=10,
                     meta=META_MAX, key="mx")
    h_sd = _svg_hist(sds_, "σ_res (3ª perna)", step=0.01, nb=10,
                     meta=META_SRES, key="sd",
                     ref=(piso_sd, f"piso MEDIANO {piso_sd:.3f}{_faixa}"))
    h_share = _svg_hist(share_, "|viés|/RMSE — quanto do erro é sistemático",
                        step=0.1, nb=10, meta=None, warn_from=0.9,
                        key="share")
    return (
        f'<h2>Onde está o erro</h2>'
        f'<p class="sub2">{n} curvas comparáveis · <b id="tri-n">{n_ok}</b> no '
        f'tripé · <b id="tri-fora">{n - n_ok}</b> fora · '
        f'<span id="tri-f100">{n_fontes_ok}</span> de {len(porf)} fontes '
        f'fechadas 100%. Tripé = <b>res.máx &le; <span class="lv" '
        f'id="lv-mx">{META_MAX:.4g}</span></b> E <b>MAE &le; <span class="lv" '
        f'id="lv-mae">{META_MAE:.4g}</span></b> E <b>σ_res &le; <span '
        f'class="lv" id="lv-sd">{META_SRES:.4g}</span></b>'
        + (f' — <b>por fonte</b> (D1, adotado 2026-07-30): o limite efetivo do '
           f'σ_res é <code>max({META_SRES:.4g}; piso medido da fonte)</code>. '
           f'Abaixo do piso, "reprovado" mediria o dado, não o modelo; era o '
           f'argumento das exceções por prova de piso, agora regra derivável.'
           if _SRES_POR_FONTE else '')
        + '.</p>'
        f'{_criterio_html(pisos, n, n_imposs_mae, n_imposs_sd, len(sds_))}'
        f'{_controles_html(META_MAE, META_MAX, META_SRES)}'
        f'<h3>Que fontes faltam (curvas fora do tripé)</h3>'
        f'{_svg_barh(rows, key="fontes")}'
        # As fontes que FECHARAM não têm barra (barra = curvas fora), então o
        # gráfico as omite por construção e o leitor via só um contador — "6 de
        # 28 fecharam 100%" sem saber QUAIS. Ausência não é informação: quem
        # fechou é justamente o que se quer saber para comparar com quem não.
        f'{_fontes_fechadas_html(porf)}{ex_barras}'
        f'<h3>Quão longe da meta</h3>'
        f'<p class="sub2">As <b>três pernas</b> do tripé, cada uma com o seu '
        f'limite e a sua escala; o quarto painel é a decomposição do erro — '
        f'<code>RMSE² = viés² + σ_res²</code> — que mostra se o que sobra é '
        f'deslocamento (nível) ou oscilação (forma).</p>'
        f'<div class="grid2">{h_mae}{h_mx}{h_sd}{h_share}</div>{ex_hist}'
        f'<h3>Qual perna é o gargalo</h3>'
        # LEGENDA DE FORMA (2026-08-01, pedido do professor): sem ela o
        # gráfico mostrava exceção, declarada e curva julgada como o MESMO
        # ponto — e a leitura "quantos estão fora" ficava sem o "de que tipo".
        f'<p class="sub2">A <b>forma</b> do ponto diz o ESTATUTO, não o erro: '
        f'<b>●</b> julgada pela régua (no tripé ou fora por mérito) · '
        f'<b>◆</b> exceção assinada (erro provado ≤ o piso do próprio dado) · '
        f'<b>■</b> declarada (a métrica ou o dado não decidem a curva) · '
        f'<b>▲</b> recortada na borda (sem estatuto) ou <b>contorno escuro</b> '
        f'na própria forma — sinal separado de propósito, porque recorte é '
        f'verdade sobre o desenho (o ponto não está onde aparece) e não sobre '
        f'a curva; os dois cabem no mesmo ponto.</p>'
        f'{_svg_scatter3(pts3, omitidas=len(trio) - len(pts3))}{ex_disp}'
        f'{_condicao_html(comp, results, pisos)}'
        f'{_graficos_replica_html(comp, results, pisos)}'
        f'{_decisao_html(comp, results, pisos)}'
        # item L (assinado 2026-08-14): "passa no tripé" e "prevê o efeito" são
        # afirmações diferentes, e até aqui a página publicava só a primeira.
        f'{_conteudo_preditivo_html(comp, results, pisos)}'
        f'{_fila_html(trio, pisos)}'
        f'{_payload_js(trio, pisos)}')


def sres_para_censo(res) -> Optional[float]:
    """σ_res COMO O CENSO deve lê-lo: `None` quando a 3ª perna não é julgável
    por falta de suporte (n < N_MIN_SRES pontos na janela da métrica — regra
    assinada 2026-08-01, prereg `2026-08-01-n-minimo-sres-prereg.md`).

    `None` aqui NÃO é "sem dado": é o sinal que `_perna_manda` já trata como
    "não-julgável ⇒ a curva não passa" (mesma convenção do σ ausente). Todo
    consumidor de censo (trio do report, página por caso, `_censo` do
    meta-teste, triagem) lê por AQUI — nunca `res.resid_std` cru — para a
    regra não poder divergir entre página e teste."""
    sd = getattr(res, "resid_std", None)
    md = getattr(res, "metric_data", None)
    # `md` VAZIO (sintético de teste / registro legado sem vetores) não é
    # "n=0": é ausência de informação sobre n — a regra só se aplica com
    # vetores presentes (pego pela suíte em 2026-08-01: 4 invariantes com
    # sintéticos de vetor vazio viravam não-julgáveis por engano).
    if sd is not None and md and len(md) < N_MIN_SRES:
        return None
    return sd


def _tripe_ok(res, lim_sd: Optional[float] = None) -> Optional[bool]:
    """Veredito da META por curva — TRÊS pernas desde 2026-07-29:
    `res.máx <= META_MAX` E `MAE <= META_MAE` E `σ_res <= META_SRES`.

    `None` quando não dá para julgar (sem simulação ou faltando uma métrica) —
    nunca contar `None` como aprovado. Atenção ao 3º caso de `None`, novo: um
    registro **sem `resid_std`** (store antigo, antes do campo) não pode ser
    julgado pela perna nova. Reprová-lo seria inventar uma medição; aprová-lo
    seria ignorar a perna. Ele vira `None` e sai do censo — se aparecerem
    muitos, o store precisa ser re-simulado, não remendado.

    `lim_sd` sobrepõe o limite da 3ª perna nesta curva. É por onde entra o piso
    POR FONTE (`limite_sres`); `None` = usa o global, que é o default e mantém o
    comportamento bit-idêntico."""
    if not (res and res.ok and res.mae is not None and res.maxerr is not None):
        return None
    if res.resid_std is None:
        return None
    # n<6 => sigma_res NAO-JULGAVEL (assinado 2026-08-01, prereg
    # 2026-08-01-n-minimo-sres): sem suporte estatistico a afirmacao de
    # 3 pernas nao pode ser feita — False (fica no censo, vira declarada),
    # NAO None (None sairia do denominador, o que esconderia a curva).
    # `md` VAZIO = sem informacao de n (sintetico/legado) => regra nao
    # se aplica (mesma guarda de `sres_para_censo`).
    md = getattr(res, "metric_data", None)
    if md and len(md) < N_MIN_SRES:
        return False
    return bool(res.maxerr <= META_MAX and res.mae <= META_MAE
                and res.resid_std <= (META_SRES if lim_sd is None else lim_sd))


# --- 3ª PERNA COM PISO POR FONTE (D1) — ✅ ADOTADO em 2026-07-30 --------------
# Prereg `docs/superpowers/specs/2026-07-29-sigma-res-por-fonte-prereg.md`,
# gates 5/5. Decisão do professor em sessão (2026-07-30): instrução "faça tudo
# que temos que fazer", dada depois de duas exposições de que D1 era o único
# bloqueio da calibração — registrada como a assinatura. Reverter = `git revert`
# do commit de adoção (a flag e TODA a fiação são inertes com False).
#
# Números RE-MEDIDOS na adoção (não os do prereg copiados):
#   G1 monotonia .... 0 curvas saem; 20 entram (19 já eram exceção assinada;
#                     nova de verdade: caccese2009_retighten_19p1mm_no_retighten)
#   censo ........... 104/202 -> 124/202
#   resolvidos ...... 124 + 25 exceções ainda necessárias = 149/202 (era 148)
#   perna que manda . σ_res 45 · res.máx 19 · MAE 14 (era 87/2/9 — o excesso
#                     do σ_res era em boa parte régua, não modelo)
#   fontes 100% ..... 7 de 28 (era 6)
#   G3 cobertura .... 6 fontes sem piso medido ficam no limite GLOBAL:
#                     LU_2024, UFU_LAB, YANG_2019, YANG_2023_AME,
#                     YANG_2023_IJPEM, ZHANG_2006 — nunca piso estimado.
#
# A regra: limite efetivo da 3ª perna = max(META_SRES, piso_σ medido da fonte)
# (`limite_sres`). O `max` garante que NUNCA aperta. As 19 exceções cobertas
# NÃO foram retiradas aqui (G4 do prereg: retirada é commit separado, assinado)
# — proposta em `New_Theory/excecoes_releitura_posD1.md`.
_SRES_POR_FONTE = True


def limite_sres(source: str, pisos: Optional[dict] = None) -> float:
    """Limite da 3ª perna para uma fonte: `max(META_SRES, piso_σ da fonte)`.

    O `max` é o coração da regra e não é detalhe de implementação: ele garante
    que a perna **nunca aperte** em relação ao limite global. Sem ele, fontes de
    piso baixo ficariam com limite MENOR que 0,025 e a mudança reprovaria curvas
    hoje aprovadas — medido: o piso puro dá 76/203 contra 105/203 de hoje, isto é
    seria uma piora de 29 curvas disfarçada de rigor.

    Fonte sem piso medido (sem réplica em condição repetida) cai no global —
    **nunca** em piso estimado, interpolado ou herdado de outra fonte (G3).
    """
    if not _SRES_POR_FONTE or not pisos:
        return META_SRES
    p = (pisos.get("por_fonte") or {}).get(source)
    return META_SRES if not p else max(META_SRES, float(p[2]))


def _trim_of(res) -> Optional[float]:
    """Janela de métrica do caso (`config_used.trim_n_max`), se houver. Com
    trim, MAE/res.máx são calculados só em N <= trim — comparar com uma curva
    inteira sem sinalizar seria comparação desigual."""
    t = (getattr(res, "config_used", None) or {}).get("trim_n_max")
    try:
        return float(t) if t is not None else None
    except (TypeError, ValueError):
        return None


def _toc_html(n_exc: int) -> str:
    """Sumário de navegação do mestre (reestruturação pedida em 2026-08-07).

    A página passou de "um painel" a um documento de ~700 kB com 8 seções, e a
    única navegação era rolar. O sumário é a parte barata da reestruturação
    que rende mais: um leitor que volta à página semanalmente vai direto ao que
    mudou. As exceções levam ★ de propósito — o professor vai destacá-las num
    artigo, e o sumário é onde esse estatuto especial fica visível primeiro."""
    itens = [("#sec-erro", "onde está o erro (3D)", ""),
             ("#sec-excecoes", f"★ exceções assinadas ({n_exc})", "exc"),
             ("#sec-orcamento", "orçamento de erro", ""),
             ("#sec-ledger", "convergência (ledger)", ""),
             ("#legendaselos", "legenda dos selos", ""),
             ("#sec-todos", "todos os casos", ""),
             ("#sec-fontes", "por fonte", "")]
    links = "".join(f'<a href="{h}"{" class=" + chr(34) + c + chr(34) if c else ""}>'
                    f'{t}</a>' for h, t, c in itens)
    # classe PRÓPRIA (`sumario`), não `toc`: o _CSS compartilhado já define
    # `.toc{position:fixed}` para a sidebar dos reports POR CASO, e a colisão
    # fazia o sumário flutuar por cima da seção de exceções (medido em
    # captura: o nav cobria o texto da introdução ao rolar).
    return f'<nav class="sumario" aria-label="seções do documento">{links}</nav>'


def _excecoes_section(records, results) -> str:
    """Exceções assinadas em SEÇÃO própria — material do artigo (2026-08-07).

    Até aqui as exceções existiam como selo espalhado nas tabelas e uma
    contagem num chip: para LER as provas era preciso caçar caso a caso. O
    professor declarou a intenção de abordá-las com destaque num artigo, o que
    muda o estatuto delas de "curvas retiradas da conta" para "achado com
    valor próprio" — cada exceção é uma curva onde está PROVADO que nem um
    modelo perfeito passaria a régua, em geral porque o erro cabe dentro da
    repetibilidade medida do próprio dado. A tabela põe caso, classe da prova,
    métricas e a prova assinada lado a lado — a leitura que um artigo precisa.

    A classe vem da ASSINATURA de origem (F5 = scatter de réplicas, S4
    2026-07-28; F7 = prova de piso, 2026-07-29), lida por membership nos dicts
    originais — não é uma coluna digitada que pode divergir deles."""
    itens = [r for r in records if r.case_id in _EXCECOES
             and caso_no_documento(r.source, r.case_id)]
    if not itens:
        return ""
    n_f5 = sum(1 for r in itens if r.case_id in _F5_EXCECOES)
    linhas = []
    for r in sorted(itens, key=lambda x: (x.source, x.case_id)):
        res = results.get(r.case_id)
        def _f(v):
            return f"{float(v):.3f}" if isinstance(v, (int, float)) else "—"
        mae = _f(res.mae if res and res.ok else None)
        mx = _f(res.maxerr if res and res.ok else None)
        sd = _f(getattr(res, "resid_std", None) if res else None)
        classe = ("réplicas (F5)" if r.case_id in _F5_EXCECOES
                  else "prova de piso (F7)")
        linhas.append(
            f'<tr><td><a href="reports/{_esc.escape(r.case_id)}.html">'
            f'{_esc.escape(r.case_id)}</a></td>'
            f'<td>{_esc.escape(NICE.get(r.source, r.source))}</td>'
            f'<td>{classe}</td><td>{mae}</td><td>{mx}</td><td>{sd}</td>'
            f'<td style="text-align:left;line-height:1.45">'
            f'{_esc.escape(_EXCECOES[r.case_id])}</td></tr>')
    return (
        f'<h2 id="sec-excecoes">★ Exceções assinadas '
        f'<span class="c">({len(itens)} curvas — material do artigo)</span></h2>'
        f'<div class="explica"><p><span class="ex-q">O que há aqui:</span> as '
        f'{len(itens)} curvas em que está <b>provado</b> que nem um modelo '
        f'perfeito passaria o tripé — o erro cabe dentro da repetibilidade '
        f'medida do próprio dado ({n_f5} por scatter de réplicas, assinatura '
        f'F5/S4 2026-07-28; {len(itens) - n_f5} por prova de piso, assinatura '
        f'F7 2026-07-29). Contam como <b>resolvidas</b>, nunca como no tripé.'
        f'</p><p class="ex-h">destaque planejado</p>'
        f'<p>Decisão do professor (2026-08-07): estas curvas serão abordadas '
        f'<b>com maior destaque em um artigo</b> — o scatter entre réplicas '
        f'nominalmente idênticas é um resultado sobre o LIMITE de qualquer '
        f'modelo determinístico de afrouxamento, não uma nota de rodapé. Esta '
        f'tabela é a leitura única: caso, prova assinada e métricas lado a '
        f'lado. No 3D acima, os losangos ◆ são estas curvas — o filtro '
        f'"◆ exceções" as isola ou as retira da vista.</p></div>'
        f'<div class="ovx"><table class="idx"><thead><tr><th>caso</th>'
        f'<th>fonte</th><th>classe da prova</th><th>MAE</th><th>res.máx</th>'
        f'<th>σ_res</th><th>prova assinada</th></tr></thead>'
        f'<tbody>{"".join(linhas)}</tbody></table></div>')


def master_report_html(records: List[CaseRecord],
                       results: Dict[str, Optional[CaseResult]]) -> str:
    labels = _case_labels()
    # Fontes retiradas saem ANTES de tudo: aqui, e não em cada tabela. Filtrar
    # `records` uma vez faz sumir a linha, o cabeçalho da fonte, o ponto no 3D,
    # o histograma, o orçamento de erro e toda contagem derivada — de graça e
    # sem chance de sobrar uma menção órfã num painel que ninguém lembrou de
    # ajustar. `n_retirados` fica para a nota de rodapé: some do documento, mas
    # o leitor tem de saber que sumiu, senão a retirada vira apagamento.
    retirados = [r for r in records if not caso_no_documento(r.source, r.case_id)]
    records = [r for r in records if caso_no_documento(r.source, r.case_id)]
    ok = [r for r in records
          if results.get(r.case_id) and results[r.case_id].ok
          and results[r.case_id].mae is not None]
    maes = [results[r.case_id].mae for r in ok]
    at_floor = sum(1 for r in ok
                   if results[r.case_id].mae <= floor_of(r.source, r.case_id) + 0.02
                   and floor_of(r.source, r.case_id) > 0)
    failed = [r for r in records
              if not results.get(r.case_id) or not results[r.case_id].ok]
    # C4: casos do usuário / exemplos sintéticos aparecem no documento mas NÃO
    # entram no censo da meta (o baseline conta 202 comparáveis, não 203).
    comp = [r for r in records if caso_comparavel(r.source, r.case_id)]
    # 3ª perna por fonte: INERTE por default (`limite_sres` devolve o global e o
    # censo fica bit-idêntico). Os pisos só são medidos quando a flag está ligada
    # — medir custa ~1 s e não faz sentido pagar por um valor que não será usado.
    _pis = (_pisos_medidos([(r.source, results[r.case_id]) for r in records
                            if results.get(r.case_id)])
            if _SRES_POR_FONTE else None)
    tripe = {r.case_id: _tripe_ok(results.get(r.case_id),
                                  limite_sres(r.source, _pis))
             for r in records}
    tripe_bool = {c: v for c, v in tripe.items() if v is not None}
    n_comp = len(comp)
    n_tri = sum(1 for r in comp if tripe.get(r.case_id) is True)
    n_fora = sum(1 for r in comp if tripe.get(r.case_id) is False)
    # A2: o store pode ser um MOSAICO de gerações (cada adoção re-simula só a
    # fonte afetada). Ler fingerprint/carimbo de UM caso afirmaria uma
    # homogeneidade que pode não existir — foi assim que o mosaico ficou
    # invisível até a auditoria de 2026-07-27.
    fps = sorted({results[r.case_id].engine_fingerprint for r in records
                  if results.get(r.case_id)
                  and results[r.case_id].engine_fingerprint})
    stamps = sorted({str(results[r.case_id].generated_at) for r in records
                     if results.get(r.case_id)
                     and results[r.case_id].generated_at})
    fp = fps[0] if len(fps) == 1 else f"{len(fps)} gerações distintas"
    stamp = stamps[0] if len(stamps) == 1 else f"{len(stamps)} carimbos"
    n_trim = sum(1 for r in records if _trim_of(results.get(r.case_id)))
    n_exc = sum(1 for r in records if r.case_id in _EXCECOES)
    n_decl = sum(1 for r in records if r.case_id in _DECLARADAS)
    # C2: gap de adoção — onde a campanha (galeria) bate o canônico adotado.
    gap = 0
    for r in ok:
        if r.gallery_entry is None:
            continue
        try:
            if float(r.gallery_entry["mae"]) < results[r.case_id].mae - 0.01:
                gap += 1
        except (KeyError, TypeError, ValueError):
            pass

    def _pernas(rec, res) -> List[Tuple[str, float, float, float]]:
        """As três pernas de uma curva: `(nome, valor, limite, múltiplo)`.

        Espelha `_tripe_ok` campo a campo de propósito — mesma métrica, mesmo
        limite, inclusive o piso POR FONTE via `limite_sres`. Reimplementar a
        comparação aqui foi exatamente o defeito medido em 2026-07-31: o selo
        julgava o MAE contra `META` (= `META_MAX` = 0,10, o alias legado) em vez
        de `META_MAE`, e **não olhava a 3ª perna**, então as curvas que reprovam
        só pelo σ_res — a perna que hoje manda em 89% das fora — saíam com um
        `✖` sem motivo e `title="viola a meta por "`. 34 selos mudos no
        documento mestre. Quem decide o veredito é `_tripe_ok`; aqui só se
        NOMEIA o que ele já decidiu."""
        if res is None:
            return []
        trio = (("MAE", res.mae, META_MAE),
                ("res.máx", res.maxerr, META_MAX),
                ("σ_res", getattr(res, "resid_std", None),
                 limite_sres(rec.source, _pis)))
        return [(nome, float(val), float(lim), float(val) / float(lim))
                for nome, val, lim in trio
                if isinstance(val, (int, float)) and lim]

    def _selo(cls: str, rotulo: str, breve: str, detalhe: str = "") -> str:
        """Um selo com tooltip RICO em `data-tip`/`data-tipx`.

        Por que não o `title` nativo (2026-07-31, pedido do professor): ele
        atrasa ~1 s, não se estiliza, trunca em algumas plataformas e — o que
        decide — **não pode conviver** com um tooltip próprio, senão o navegador
        desenha os dois. A descrição vai para `data-tip` (breve, a primeira
        linha) + `data-tipx` (os números do caso) e o `aria-label` carrega as
        duas juntas, para leitor de tela não perder o que o hover mostra."""
        # SEM `tabindex`, e a decisão é MEDIDA, não estética: com os selos
        # focalizáveis a página passava a ter 687 paradas de Tab, **256 delas
        # (37%) selos** — atravessar a lista pelo teclado ficaria 1,6x mais
        # longo. O que o tooltip acrescenta para quem enxerga já está na
        # própria linha (as colunas MAE / res.máx / σ_res mostram os três
        # valores); o que ele acrescenta de novo — qual perna MANDA — está na
        # legenda. É o mesmo critério que manteve os pontos do 3D fora da ordem
        # de tab, com rota alternativa (§ leitor de foco). O `aria-label` fica:
        # leitor de tela anuncia `aria-label` em modo de leitura sem precisar
        # de foco, então a rota assistiva não depende do `tabindex`.
        aria = f"{breve} {detalhe}".strip()
        dx = (f' data-tipx="{_esc.escape(detalhe, quote=True)}"'
              if detalhe else "")
        return (f'<span class="bdg {cls}"'
                f' data-tip="{_esc.escape(breve, quote=True)}"{dx}'
                f' aria-label="{_esc.escape(aria, quote=True)}">'
                f'{rotulo}</span>')

    def _badges(rec, res) -> str:
        out = []
        v = tripe.get(rec.case_id)
        pernas = _pernas(rec, res)
        if v is True:
            ap = max(pernas, key=lambda p: p[3], default=None)
            det = (f"Perna mais apertada: {ap[0]} em {ap[3]:.2f}× o limite "
                   f"({ap[1]:.4g} de {ap[2]:.4g})." if ap else "")
            out.append(_selo(
                "ok", "&#10004; tripé",
                "Passa nas três pernas ao mesmo tempo — é o único selo que "
                "significa acerto do modelo.", det))
        elif v is False:
            viol = [p for p in pernas if p[3] > 1.0]
            # regra n<6: sigma NAO-JULGAVEL nunca e' violacao NOMEADA (o
            # valor nao tem suporte); o selo lista so as pernas julgaveis
            # violadas, e "σ n<6" quando nenhuma outra viola.
            if sres_para_censo(res) is None:
                viol = [p for p in viol if p[0] != "σ_res"]
            if not viol and sres_para_censo(res) is None \
                    and getattr(res, "resid_std", None) is not None:
                # estado NOVO e legitimo (regra n<6, 2026-08-01): reprova sem
                # perna excedida porque o sigma nao e' julgavel — nomear, nao
                # cair no "fora (?)" (que significa divergencia selo-juiz)
                n_md = len(getattr(res, "metric_data", None) or [])
                breve = (f"Fora do tripé por σ_res NÃO-JULGÁVEL: n={n_md} < "
                         f"{N_MIN_SRES} pontos na janela (regra assinada "
                         f"2026-08-01).")
                det = ("As pernas julgáveis (MAE, res.máx) passam; a "
                       "afirmação de tripé exige as três. Reabre com dado "
                       "denso.")
                lab = "σ n&lt;6"
            elif viol:
                manda = max(viol, key=lambda p: p[3])
                nums = " · ".join(f"{n} {val:.4g} de {lim:.4g} ({m:.2f}×)"
                                  for n, val, lim, m in viol)
                breve = (f"Reprova a meta: {len(viol)} de 3 pernas fora. "
                         f"Quem manda é {manda[0]}, em {manda[3]:.2f}× o "
                         f"limite.")
                det = (f"{nums}. Manda = o maior múltiplo do limite, logo é a "
                       f"perna que sustenta a reprovação mesmo quando outras "
                       f"também violam.")
                lab = "+".join(n for n, *_ in viol)
            else:
                # Não deve acontecer: `v is False` só sai de `_tripe_ok` quando
                # alguma perna excede. Se aparecer, é divergência selo-juiz e
                # tem de GRITAR, não virar um "fora" genérico — foi o silêncio
                # que deixou os 34 selos mudos passarem.
                breve = ("DIVERGÊNCIA: o veredito reprova mas nenhuma perna "
                         "excede o limite.")
                det = "Re-simule o store — selo e juiz discordam."
                lab = "fora (?)"
            out.append(_selo("no", f"&#10006; {lab}", breve, det))
        t = _trim_of(res)
        if t:
            out.append(_selo(
                "tr", f"trim N&#8804;{t:g}",
                f"A métrica foi calculada só até N = {t:g} — o trecho seguinte "
                f"é feição out-of-model documentada.",
                "Recorte por julgamento humano, ratificado na assinatura da "
                "F5; entra na assinatura, não é ajuste livre."))
        exc = _EXCECOES.get(rec.case_id)
        if exc:
            out.append(_selo(
                "ex", "exceção",
                "Exceção ASSINADA: está provado que nem um modelo perfeito "
                "passaria o limite aqui. Conta como resolvida, não como no "
                "tripé.",
                f"{exc} (S4 2026-07-28 / F7 2026-07-29)."))
        dec = _DECLARADAS.get(rec.case_id)
        if dec:
            out.append(_selo(
                "tr", "declarada",
                "DECLARADA: a métrica ou o dado não decidem esta curva — "
                "declarar não é acerto do modelo.",
                f"{dec} (camada 2 da regra de parada, assinada por delegação "
                f"2026-07-30)."))
        return "".join(out)

    def _flags(rec, res, lab) -> str:
        f = []
        v = tripe.get(rec.case_id)
        if v is True:
            f.append("tripe")
        elif v is False:
            f.append("fora")
        if _trim_of(res):
            f.append("trim")
        if rec.case_id in _EXCECOES:
            f.append("excecao")
        if lab:
            f.append(str(lab))
        return " ".join(f)

    def _row_tr(r, com_fonte: bool = False) -> str:
        res = results.get(r.case_id)
        meta_lab = labels.get(r.case_id) or {}
        lab = meta_lab.get("label", "")
        ev = meta_lab.get("evidence", "")
        if res and res.ok and res.mae is not None:
            fl = floor_of(r.source, r.case_id)
            lim = max(fl + 0.02, META)
            cls = "good" if res.mae <= lim else "warn"
            # C3: com piso de repetibilidade, o verde vai ATÉ lim > META — a
            # célula verde aqui significa "no piso do dado", não "na meta".
            ttl = (f' title="verde até {lim:.3f}: piso de repetibilidade do '
                   f'dado {fl:.3f} + 0.02, acima da meta {META:.2f}"'
                   if fl > 0 else "")
            mae_td = f'<td class="{cls}"{ttl}>{res.mae:.3f}</td>'
        elif res and res.ok:
            mae_td = '<td>—</td>'
        else:
            mae_td = '<td class="warn">erro</td>'
        if res and res.ok and res.maxerr is not None:
            mcls = "warn" if res.maxerr > META else "good"
            mx_td = f'<td class="{mcls}">{res.maxerr:.3f}</td>'
        else:
            mx_td = '<td>—</td>'
        sd = getattr(res, "resid_std", None) if res else None
        sd_td = (f'<td>{float(sd):.3f}</td>'
                 if isinstance(sd, (int, float)) else '<td>—</td>')
        g = "—"
        if r.gallery_entry is not None:
            try:
                g = f'{float(r.gallery_entry["mae"]):.3f}'
            except (KeyError, TypeError, ValueError):
                g = "—"
        diag = (f'<span title="{_esc.escape(str(ev))}">{lab}</span>'
                if lab else "—")
        src_td = f'<td>{NICE.get(r.source, r.source)}</td>' if com_fonte else ""
        return (f'<tr data-flags="{_flags(r, res, lab)}">'
                f'<td><a href="reports/{r.case_id}.html">{r.case_id}</a>'
                f'{_badges(r, res)}</td>{src_td}'
                f'<td>{_FAM_PT.get(r.family, r.family)}</td>'
                f'<td>{_CLASS_PT.get(r.case_class, r.case_class)}</td>'
                f'{mae_td}{mx_td}{sd_td}<td>{diag}</td><td>{g}</td></tr>')

    def _hdr(com_fonte: bool = False) -> str:
        f_th = "<th>fonte</th>" if com_fonte else ""
        return (f'<thead><tr><th>caso</th>{f_th}<th>família</th><th>classe</th>'
                f'<th>MAE</th><th>res.máx</th><th>σ_res</th>'
                f'<th>diagnóstico</th><th>campanha</th></tr></thead>')

    def _legenda_selos() -> str:
        """Toggle com o significado dos selos que aparecem na frente dos casos.

        Pedido do professor (2026-07-31). Até aqui os selos eram legíveis só
        pelo atributo `title` — hover, que **não existe em toque** e não sai na
        impressão —, então o vocabulário da lista mestre era invisível para quem
        não passasse o mouse item por item.

        As contagens saem do MESMO store que desenha as linhas, calculadas na
        geração: legenda com número escrito à mão envelhece sozinha (§4.43) e
        este arquivo já tem um teste que persegue exatamente isso
        (`test_meta_numeros_nao_envelhecem`). Contam-se CASOS, não `<span>`s —
        cada caso é desenhado duas vezes no documento (na tabela única e na
        tabela da sua fonte), e contar spans daria o dobro."""
        ids_ok = {r.case_id for r in records if tripe.get(r.case_id) is True}
        n_ok = len(ids_ok)
        # A coluna conta os selos DESENHADOS (todos os registros); o chip do topo
        # conta o CENSO DA META (só os comparáveis). Hoje diferem em 1 — o
        # `exemplo_m12_sintetico`, fonte USER, que passa no tripé e não entra no
        # censo. Deixar os dois números soltos na mesma página, sem dizer que
        # medem populações diferentes, é fabricar uma contradição aparente.
        _cids_comp = {r.case_id for r in comp}

        def _censo_nota(ids: set) -> str:
            """Nomeia os casos que levam o selo mas ficam FORA do censo da meta.

            Não basta contar: o censo exclui por DOIS motivos distintos (fonte
            em `_SRC_NAO_COMPARAVEL` e caso em `_CID_NAO_COMPARAVEL`, este
            criado em 2026-07-31 para a duplicata do Lu). Uma nota que citasse
            só a fonte estaria errada por omissão — foi o que escrevi primeiro,
            e o número 201 vs 202 denunciou."""
            fora = sorted(ids - _cids_comp)
            if not fora:
                return ""
            det = "; ".join(
                f'<code>{_esc.escape(c)}</code> &#8212; '
                f'{_esc.escape(_CID_NAO_COMPARAVEL.get(c, "fonte não comparável"))}'
                for c in fora)
            return (f' Destes, <b>{len(ids) - len(fora)}</b> entram no censo da '
                    f'meta (de {len(comp)} comparáveis); {len(fora)} fica'
                    f'{"m" if len(fora) > 1 else ""} fora do censo: {det}.')
        combo: Dict[str, int] = {}
        manda: Dict[str, int] = {}
        ids_fora = set()
        for r in records:
            if tripe.get(r.case_id) is not False:
                continue
            viol = [p for p in _pernas(r, results.get(r.case_id)) if p[3] > 1.0]
            if not viol:
                continue
            ids_fora.add(r.case_id)
            chave = "+".join(n for n, *_ in viol)
            combo[chave] = 1 + combo.get(chave, 0)
            top = max(viol, key=lambda p: p[3])[0]
            manda[top] = 1 + manda.get(top, 0)
        n_fora_sel = len(ids_fora)
        cb = " · ".join(f"<code>{_esc.escape(k)}</code> {v}"
                        for k, v in sorted(combo.items(), key=lambda kv: -kv[1]))
        mb = " · ".join(f"<b>{_esc.escape(k)}</b> {v}"
                       for k, v in sorted(manda.items(), key=lambda kv: -kv[1]))
        n_tr = sum(1 for r in records if _trim_of(results.get(r.case_id)))
        n_ex = sum(1 for r in records if r.case_id in _EXCECOES)
        n_de = sum(1 for r in records if r.case_id in _DECLARADAS)
        sd_lo, sd_hi = META_SRES, META_SRES
        # `if vals` e não só `if _pis`: `records` pode ficar VAZIO (documento só
        # com fontes retiradas, ou um teste que monta o mestre com 1 registro
        # que por acaso é de fonte retirada) e aí `min()` estoura. O default
        # META_SRES já é a leitura correta quando não há fonte alguma.
        vals = ([limite_sres(s, _pis) for s in {r.source for r in records}]
                if _pis else [])
        if vals:
            sd_lo, sd_hi = min(vals), max(vals)
        sd_txt = (f'max({META_SRES:.4g}; piso da fonte) — hoje de '
                  f'<b>{sd_lo:.4g}</b> a <b>{sd_hi:.4g}</b> conforme a fonte'
                  if sd_hi > sd_lo else f'<b>{META_SRES:.4g}</b>')
        linhas = [
            ('<span class="bdg ok">&#10004; tripé</span>',
             f'Passa nas <b>três</b> pernas ao mesmo tempo: res.máx &le; '
             f'<b>{META_MAX:.4g}</b> <i>e</i> MAE &le; <b>{META_MAE:.4g}</b> '
             f'<i>e</i> σ_res &le; {sd_txt}. É o único selo que significa '
             '<b>acerto do modelo</b>. O hover diz qual perna está mais '
             'apertada e a que fração do limite ela chegou.'
             + _censo_nota(ids_ok), n_ok),
            ('<span class="bdg no">&#10006; MAE+σ_res</span>',
             'Reprova. O rótulo nomeia <b>todas</b> as pernas que estouraram '
             f'(combinações vivas: {cb or "—"}); o hover traz valor, limite e '
             'múltiplo de cada uma e diz qual <b>manda</b> — a de maior '
             'múltiplo, que é a que sustenta a reprovação mesmo quando outras '
             f'também violam. Manda hoje: {mb or "—"}.'
             + _censo_nota(ids_fora) +
             ' As duas leituras são '
             'perguntas diferentes: <i>"viola só esta"</i> diz onde consertar '
             'uma perna fecha a curva; <i>"esta manda"</i> diz quem segura o '
             'veredito.', n_fora_sel),
            ('<span class="bdg tr">trim N&#8804;…</span>',
             'A métrica foi calculada só até aquele N — o trecho seguinte é '
             'feição <b>out-of-model</b> documentada (fratura, colapso '
             'quase-vertical, debris). Recorte por julgamento humano, '
             'ratificado na assinatura da F5; entra na assinatura, não é '
             'ajuste livre.', n_tr),
            ('<span class="bdg ex">exceção</span>',
             'Exceção <b>ASSINADA</b> (F5/S4 2026-07-28 e F7 por prova de piso '
             '2026-07-29): está provado que nem um modelo perfeito passaria o '
             'limite ali, em geral porque o erro já cabe dentro da '
             'repetibilidade medida da própria fonte. Conta como '
             '<b>resolvida</b> — <b>não</b> como no tripé.', n_ex),
            ('<span class="bdg tr">declarada</span>',
             'Camada 2 da regra de parada (assinada por delegação '
             '2026-07-30): a <b>métrica ou o dado</b> não decidem — n&lt;6 '
             'pontos (σ_res sem suporte) ou colapso quase-vertical '
             '(Δdado&gt;0,25 entre pontos). Sai da fila com procedência e '
             '<b>não é acerto do modelo</b>.', n_de),
        ]
        # `text-align:left` explícito: `.idx td` alinha à DIREITA (a tabela foi
        # desenhada para colunas numéricas) e só o `:first-child` volta à
        # esquerda. Sem isto a coluna de prosa sai justificada à direita —
        # ilegível em parágrafo, e invisível no HTML: só apareceu na captura de
        # tela. `line-height` porque são 4-8 linhas por célula, não um número.
        trs = "".join(f'<tr><td>{sel}</td>'
                      f'<td style="text-align:left;line-height:1.5">{txt}</td>'
                      f'<td><b>{n}</b></td></tr>'
                      for sel, txt, n in linhas)
        return (
            '<details id="legendaselos"><summary>o que significam os selos na '
            'frente de cada caso (✔ tripé · ✖ perna · trim · exceção · '
            'declarada)</summary>'
            '<div class="ovx"><table class="idx"><thead><tr><th>selo</th>'
            '<th>o que significa</th><th>casos</th></tr></thead>'
            f'<tbody>{trs}</tbody></table></div>'
            '<p class="sub2"><b>Passar o mouse</b> em qualquer selo mostra '
            'esta mesma descrição em resumo, já com os números <i>daquela</i> '
            'curva — valor, limite e múltiplo de cada perna, e qual delas '
            'manda. Esta tabela existe para as leituras que o hover não cobre: '
            'em tela de toque não há hover, ela sai na impressão, e os selos '
            'não entram na ordem de Tab de propósito (seriam <b>256 de 687</b> '
            'paradas — os três valores já estão nas colunas da linha). '
            'Um caso pode levar <b>mais de um</b> selo (p.ex. '
            'Um caso pode levar <b>mais de um</b> selo (p.ex. '
            'reprovar e ter trim), então a coluna não soma o total. Cada caso '
            'aparece duas vezes no documento — na tabela única e na tabela da '
            'sua fonte —, e a contagem aqui é de <b>casos</b>, não de selos '
            'desenhados. Os números são recomputados do store a cada geração; '
            'o veredito de cada perna sai de <code>_tripe_ok</code>, o mesmo '
            'que decide o censo da meta.</p></details>')

    if maes:
        n_mx = sum(1 for r in ok if (results[r.case_id].maxerr or 0) > META)
        pct = (100.0 * n_tri / n_comp) if n_comp else 0.0
        # A1: o número que governa a campanha é o AND dos dois critérios — e
        # até 2026-07-27 ele não aparecia em lugar nenhum da página.
        chips = (f'<div class="chips">'
                 f'<span class="chip big">no tripé <b>{n_tri}/{n_comp}</b> '
                 f'({pct:.0f}%)</span>'
                 f'<span class="chip">fora do tripé <b>{n_fora}</b></span>'
                 f'<span class="chip" title="casos do usuário e exemplos '
                 f'sintéticos entram no documento, mas não no censo da meta">'
                 f'casos de validação <b>{len(records)}</b> · comparáveis '
                 f'<b>{n_comp}</b></span>'
                 f'<span class="chip">MAE médio <b>{np.mean(maes):.3f}</b></span>'
                 f'<span class="chip">mediana <b>{np.median(maes):.3f}</b></span>'
                 f'<span class="chip" title="MAE dentro do piso de '
                 f'repetibilidade medido entre réplicas do próprio dado">'
                 f'no piso do dado <b>{at_floor}</b></span>'
                 f'<span class="chip">res.máx &gt;{META:.2f} <b>{n_mx}</b> '
                 f'(meta: 0)</span>'
                 f'<span class="chip" title="métrica calculada em janela '
                 f'recortada — ratificados pela assinatura da F5">'
                 f'com trim <b>{n_trim}</b></span>'
                 f'<span class="chip" title="ASSINADAS: F5 em 2026-07-28 '
                 f'(S4) + F7 por prova de piso em 2026-07-29. A união é um dict '
                 f'de leitura única — 9 curvas estão nos dois documentos e não '
                 f'contam duas vezes.">'
                 f'exceções assinadas <b>{n_exc}</b> · '
                 f'declaradas <b>{n_decl}</b></span>'
                 f'<span class="chip" title="casos onde a campanha bate o '
                 f'canônico adotado em mais de 0.01 de MAE">'
                 f'gap de adoção <b>{gap}</b></span>'
                 f'<span class="chip">não simuláveis <b>{len(failed)}</b></span>'
                 f'</div>')
        # C1: partida -> hoje -> alvo, na mesma escala.
        marca = (100.0 * _PARTIDA_TRIPE / n_comp) if n_comp else 0.0
        barra = (f'<div class="prog"><div class="prog-f" '
                 f'style="width:{max(0.0, min(100.0, pct)):.1f}%"></div>'
                 f'<div class="prog-m" '
                 f'style="left:{max(0.0, min(100.0, marca)):.1f}%"></div></div>'
                 f'<p class="sub2">progresso da meta: partida '
                 f'<b>{_PARTIDA_TRIPE}</b> (marca) &rarr; hoje <b>{n_tri}</b> '
                 f'&rarr; alvo <b>{n_comp}</b> menos as exceções assinadas. '
                 f'<b>Atenção à régua:</b> a partida foi medida no tripé de '
                 f'<b>duas</b> pernas (MAE e res.máx &le; 0,10) e o "hoje" está '
                 f'no de <b>três</b> (res.máx {META_MAX:.4g} · MAE '
                 f'{META_MAE:.4g} · σ_res {META_SRES:.4g}, régua de '
                 f'2026-07-29) — a diferença entre os dois números NÃO é '
                 f'progresso nem regressão do modelo, é troca de critério. '
                 f'Comparar só dentro da mesma régua.</p>')
        het = ""
        if len(fps) > 1:
            mostra = ", ".join(fps[:6]) + ("…" if len(fps) > 6 else "")
            het = (f'<p class="alert"><b>Store heterogêneo</b>: convivem aqui '
                   f'{len(fps)} fingerprints de engine ({mostra}) e '
                   f'{len(stamps)} carimbos de geração. Cada adoção re-simulou '
                   f'só a fonte afetada, então estes números vêm de gerações '
                   f'de configuração diferentes. Certificar exige um '
                   f'<code>report --all</code> que re-carimbe tudo com um '
                   f'fingerprint único.</p>')
        head = (chips + barra + het +
                f'<p class="sub">gerado em {stamp} &#183; engine {fp}. Cada '
                f'linha abre o <b>report individual completo</b> (condições '
                f'de contorno, modelo MSD, curvas interativas, decomposição '
                f'por mecanismo, constantes com proveniência). Clique nos '
                f'cabeçalhos das colunas para ordenar.</p>')
    else:
        head = (f'<p class="sub">{len(records)} casos de validação &#183; '
                f'nenhum resultado com MAE no cache ainda — rode o CLI --all.</p>')
    # B4: o documento de acompanhamento tem de dizer o que espera decisão.
    head += (f'<div class="verd"><b>Exceções ASSINADAS</b> ({n_exc}) — '
             f'<a href="../f5_excecoes_propostas.md">F5</a> (assinada 2026-07-28, '
             f'S4 8/8) &#183; '
             f'<a href="../f7_excecoes_por_prova_de_piso.md">F7 por prova de '
             f'piso</a> (assinada 2026-07-29: o erro do modelo cabe dentro da '
             f'repetibilidade MEDIDA da fonte, logo nem um modelo perfeito '
             f'passaria o limite ali). Curva coberta por exceção conta como '
             f'<b>resolvida</b>, não como no tripé. <b>DECLARADAS</b> '
             f'({n_decl}, camada 2 da <a href="../regra_de_parada_proposta.md">'
             f'regra de parada</a>, assinada por delegação 2026-07-30): curvas '
             f'em que a <i>métrica ou o dado</i> não decidem — n&lt;6 pontos '
             f'(σ_res sem suporte) ou colapso quase-vertical (Δdado&gt;0,25 '
             f'entre pontos, §4.44–48a). Declarada ≠ acerto do modelo. '
             f'<b>Leitura DUPLA, sempre junta:</b> estrita (tripé) '
             f'<b>{n_tri} de {n_comp}</b> &#183; resolvida/declarada '
             f'<b>{n_tri} + {n_exc} + {n_decl} = {n_tri + n_exc + n_decl} de '
             f'{n_comp}</b>. '
             f'Segue aberto: <a href="../DECISOES_PENDENTES.md">fila de decisões '
             f'de forma</a> (26 form-limited) &#183; 15 indecidíveis sem piso '
             f'(1 réplica por fonte destrava) &#183; as 33 RECUSADAS por prova '
             f'de piso &#183; '
             f'<a href="../../.superpowers/master-0p1-progress.md">ledger '
             f'mestre</a>.</div>')
    head += ('<p><a href="all_plots.html"><b>→ todos os gráficos</b></a> '
             '(dado × modelo, 1 gráfico por caso, agrupados por fonte)</p>'
             '<p class="qfs">'
             '<input id="filtro" type="search" '
             'placeholder="filtrar casos por nome, fonte, família…">'
             '<button type="button" class="qf" data-f="fora">só fora do tripé</button>'
             '<button type="button" class="qf" data-f="forma">só forma</button>'
             '<button type="button" class="qf" data-f="nivel">só nível</button>'
             '<button type="button" class="qf" data-f="excecao">só exceções</button>'
             '<button type="button" class="qf" data-f="trim">só com trim</button>'
             '</p>')
    # A legenda vem DEPOIS dos filtros e ANTES das tabelas de propósito: é o
    # ponto em que o leitor acabou de ganhar um botão ("só fora do tripé") e
    # ainda não viu um selo. Fechada por default — quem já conhece o vocabulário
    # não paga rolagem por ele.
    head += _legenda_selos()
    rmses = [float(r.rmse) for r in results.values()
             if r is not None and r.ok and r.rmse is not None]
    head += ('<div id="sec-erro"></div>' + _erro_section(comp, results)
             + _excecoes_section(records, results)
             + '<div id="sec-orcamento"></div>' + _budget_section(tripe_bool)
             + '<div id="sec-ledger"></div>'
             + _ledger_section(n_comp,
                               float(np.mean(maes)) if maes else None,
                               float(np.mean(rmses)) if rmses else None))
    body = [head]
    # B2: visão única ordenável — sem ela não dá para achar os piores casos
    # sem varrer as tabelas por fonte uma a uma.
    todos = "".join(_row_tr(r, True)
                    for r in sorted(records, key=lambda z: z.case_id))
    body.append(
        f'<h2 id="sec-todos">Todos os casos <span class="c">(tabela única, ordenável)</span></h2>'
        f'<details id="tabelatodos"><summary>abrir os {len(records)} casos '
        f'numa tabela só — '
        f'clique num cabeçalho para ordenar (ex.: res.máx decrescente)</summary>'
        f'<div class="ovx"><table class="idx">{_hdr(True)}'
        f'<tbody>{todos}</tbody></table></div></details>')
    by_src: Dict[str, List[CaseRecord]] = {}
    for r in records:
        by_src.setdefault(r.source, []).append(r)
    body.append('<div id="sec-fontes"></div>')
    for src in sorted(by_src):
        items = by_src[src]
        src_maes = [results[r.case_id].mae for r in items
                    if results.get(r.case_id) and results[r.case_id].ok
                    and results[r.case_id].mae is not None]
        mean_txt = f" &#183; MAE médio {np.mean(src_maes):.3f}" if src_maes else ""
        n_jul = sum(1 for r in items if tripe.get(r.case_id) is not None)
        n_ts = sum(1 for r in items if tripe.get(r.case_id) is True)
        tri_txt = f" &#183; no tripé {n_ts}/{n_jul}" if n_jul else ""
        trs = "".join(_row_tr(r) for r in sorted(items, key=lambda z: z.case_id))
        body.append(
            f'<h2>{NICE.get(src, src)} <span class="c">({len(items)} casos'
            f'{mean_txt}{tri_txt})</span></h2>'
            f'<div class="ovx"><table class="idx">{_hdr()}'
            f'<tbody>{trs}</tbody></table></div>')
    if failed:
        lis = "".join(
            f'<li><a href="reports/{r.case_id}.html">{r.case_id}</a> — '
            f'{(results.get(r.case_id).error if results.get(r.case_id) else "nunca simulado — rode o CLI --all")}</li>'
            for r in failed)
        body.append(f'<h2>Não simuláveis (degradação honesta)</h2><ul>{lis}</ul>')
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Casos de validação — documento mestre</title>{_CSS}
<style>/* controles ao vivo dos limites + justificativa técnica (2026-07-29).
 Vive AQUI e não no _CSS compartilhado de propósito: o _CSS é embutido nos 203
 reports por caso, e regras que só o mestre usa inflariam 203 arquivos a cada
 ajuste de estilo (medido: 24 linhas x 203 arquivos de diff puro, zero efeito). */
.ctl{{display:flex;flex-wrap:wrap;align-items:center;gap:14px;margin:10px 0 4px;
 padding:10px 12px;border:1px solid var(--bd);border-radius:8px;
 background:var(--card)}}
.ctl-t{{font-weight:600;font-size:.86rem;color:var(--accent);
 text-transform:uppercase;letter-spacing:.04em}}
.ctl label{{display:flex;align-items:center;gap:6px;font-size:.86rem}}
.ctl input[type=range]{{width:104px;accent-color:var(--di)}}
.ctl output{{font-variant-numeric:tabular-nums;font-weight:600;min-width:3.4em;
 color:var(--di)}}
.ctl select,.ctl button{{font:inherit;font-size:.84rem;padding:2px 6px;
 border:1px solid var(--bd);border-radius:5px;background:var(--bg);
 color:var(--fg)}}
.ctl button{{cursor:pointer}}
.ctl-h{{font-size:.78rem;color:var(--mut);flex-basis:100%}}
/* tooltip dos selos (2026-07-31). `position:fixed` porque os selos vivem
   dentro de `div.ovx` (overflow-x:auto), que RECORTA qualquer caixa absoluta —
   e `pointer-events:none` para o tooltip nunca interceptar o clique do link do
   caso que fica ao lado dele. */
.tipbox{{position:fixed;z-index:60;max-width:44ch;pointer-events:none;
 background:var(--card);color:var(--fg);border:1px solid var(--bd);
 border-left:3px solid var(--accent);border-radius:7px;padding:7px 10px;
 font-size:.78rem;line-height:1.45;
 box-shadow:0 6px 20px rgba(0,0,0,.28)}}
.tipbox[hidden]{{display:none}}
.tip-b{{font-weight:600}}
.tip-x{{margin-top:4px;color:var(--mut);font-size:.74rem;
 font-variant-numeric:tabular-nums}}
/* `cursor:help` e' o unico aviso de que ha' algo sob o mouse — o selo nao e'
   focalizavel de proposito (256 de 687 paradas de Tab seriam selos; ver o
   comentario em `_selo`), entao nao ha anel de foco a estilizar. */
.bdg[data-tip]{{cursor:help}}
/* sumário de navegação (2026-08-07). Classe própria: `.toc` do _CSS
   compartilhado é a sidebar FIXA dos reports por caso, e a colisão punha
   este nav flutuando por cima das seções. */
.sumario{{display:flex;flex-wrap:wrap;gap:6px 16px;margin:8px 0 14px;
 padding:8px 12px;border:1px solid var(--bd);border-radius:8px;
 background:var(--card);font-size:.82rem}}
.sumario a{{color:var(--accent);text-decoration:none}}
.sumario a:hover{{text-decoration:underline}}
.sumario a.exc{{font-weight:700}}
/* leitor de foco do 3D: altura FIXA (min-height) de propósito — sem ela a linha
   aparece/desaparece com o hover e empurra o gráfico, e o ponto sob o cursor
   sai de baixo dele (o gráfico "fugia do mouse"). */
.s3i{{font-size:.8rem;color:var(--mut);min-height:1.5em;margin:2px 0 8px;
 padding:4px 8px;border-left:2px solid var(--bd);overflow-wrap:anywhere}}
.s3i code{{font-family:Consolas,monospace;color:var(--accent)}}
.s3i b{{color:var(--fg);font-variant-numeric:tabular-nums}}
.s3i .s3f{{color:var(--mut)}}
svg[data-s3]{{outline-offset:2px}}
@media print{{.s3i{{display:none}}}}
.lv{{font-variant-numeric:tabular-nums;color:var(--di)}}
.crit{{margin:10px 0;padding:10px 12px;border:1px solid var(--bd);
 border-radius:8px;background:var(--card)}}
.crit>summary{{cursor:pointer;font-size:.94rem}}
.crit h4{{margin:16px 0 6px;font-size:.92rem}}
.crit table{{margin:6px 0 10px}}
@media print{{.ctl{{display:none}}.crit{{border:0;padding:0}}
 .crit>summary{{list-style:none}}}}
@media(max-width:760px){{.ctl input[type=range]{{width:80px}}}}
.idx{{margin:2px 0 6px}}.idx th{{text-align:right;color:var(--mut);font-weight:600;
 padding:4px 8px;border-bottom:1px solid var(--bd);font-size:.75rem}}
.idx th:first-child{{text-align:left}}.idx td{{text-align:right}}.idx td:first-child{{text-align:left}}
.idx td a{{color:var(--accent);text-decoration:none;font-family:Consolas,monospace}}
.idx .good{{color:var(--good);font-weight:600}}.idx .warn{{color:var(--warn);font-weight:600}}
h2 .c{{font-size:.72rem;color:var(--mut);text-transform:none;letter-spacing:0}}
.chip.big{{border-color:var(--accent);color:var(--accent);font-size:.86rem}}
.alert{{background:var(--card);border:1px solid var(--warn);
 border-left:3px solid var(--warn);border-radius:8px;padding:8px 12px;
 font-size:.82rem;margin:6px 0 10px;max-width:95ch}}
.alert code{{font-family:Consolas,monospace}}
.bdg{{display:inline-block;font-size:.66rem;padding:1px 6px;margin-left:6px;
 border-radius:999px;border:1px solid var(--bd);white-space:nowrap;
 font-family:-apple-system,"Segoe UI",sans-serif}}
.bdg.ok{{color:var(--good);border-color:var(--good)}}
.bdg.no{{color:var(--warn);border-color:var(--warn)}}
.bdg.tr{{color:var(--mut)}}
.bdg.ex{{color:var(--accent);border-color:var(--accent)}}
.qfs{{display:flex;flex-wrap:wrap;gap:6px;align-items:center}}
.qfs input{{flex:1 1 260px;padding:5px 10px;border:1px solid var(--bd);
 border-radius:999px;background:var(--card);color:var(--fg);font:inherit;
 font-size:.8rem}}
button.qf{{background:var(--card);color:var(--mut);border:1px solid var(--bd);
 border-radius:999px;padding:4px 12px;font:inherit;font-size:.74rem;
 cursor:pointer}}
button.qf:hover{{color:var(--fg);border-color:var(--accent)}}
button.qf.on{{color:var(--bg);background:var(--accent);border-color:var(--accent)}}
.prog{{position:relative;height:10px;background:var(--card);
 border:1px solid var(--bd);border-radius:999px;margin:2px 0 4px}}
.prog-f{{height:100%;background:var(--good);opacity:.75;border-radius:999px}}
.prog-m{{position:absolute;top:-3px;width:2px;height:16px;background:var(--mut)}}
details>summary{{cursor:pointer;color:var(--mut);font-size:.8rem;margin:4px 0}}
.explica{{background:var(--card);border:1px solid var(--bd);
 border-left:3px solid var(--accent);border-radius:8px;padding:10px 14px;
 margin:2px 0 18px;font-size:.82rem;max-width:95ch}}
.explica p{{margin:4px 0}}
.explica ul{{margin:4px 0 8px;padding-left:20px}}
.explica li{{margin:2px 0}}
.explica code{{font-family:Consolas,monospace}}
.ex-q{{font-weight:600}}
.ex-h{{color:var(--mut);text-transform:uppercase;letter-spacing:.05em;
 font-size:.68rem;margin-top:9px !important}}</style>
</head><body>{_topbar("Casos de validação — documento mestre",
                      f'<span class="chip">no tripé {n_tri}/{n_comp}</span>'
                      f'<span class="chip">{len(records)} casos</span>')}<div class="wrap">
<h1>Casos de validação — documento mestre</h1>
{_toc_html(n_exc)}
{"".join(body)}
{_nota_retirados(retirados)}<p class="foot">Reports individuais em reports/.
 Gerado por bolt_analysis_studio.validation.report_html do validation_store +
 core.validation_cases + adopted_configs + bloco shared canônico.</p>
</div>{_CHART_JS}{_MASTER_JS}{_TIP_JS}</body></html>'''


def _dec_xy(x, y, m: int = 220):
    """Decima p/ ate m pontos (1o e ultimo sempre) — controla o tamanho da
    pagina all_plots (178 graficos)."""
    x = np.asarray(x, dtype=float); y = np.asarray(y, dtype=float)
    if len(x) <= m:
        return [float(v) for v in x], [float(v) for v in y]
    idx = np.unique(np.linspace(0, len(x) - 1, m).astype(int))
    return [float(x[i]) for i in idx], [float(y[i]) for i in idx]


def all_plots_html(records: List[CaseRecord],
                   results: Dict[str, Optional[CaseResult]]) -> str:
    """Pagina unica com TODOS os graficos dado x modelo (pedido do professor
    2026-07-14), do store canonico — grade por fonte, cada card linka o
    report individual completo."""
    # Mesmo filtro do mestre: uma fonte retirada não pode sobreviver aqui. Esta
    # página é linkada do mestre como "todos os gráficos" — deixar o UFU só
    # nela seria pior que não retirar, porque a contradição ficaria a um clique.
    records = [r for r in records if caso_no_documento(r.source, r.case_id)]
    by_src: Dict[str, List[CaseRecord]] = {}
    for r in records:
        by_src.setdefault(r.source, []).append(r)
    body: List[str] = []
    for src in sorted(by_src, key=lambda s: NICE.get(s, s).lower()):
        items = sorted(by_src[src], key=lambda z: z.case_id)
        maes = [results[r.case_id].mae for r in items
                if results.get(r.case_id) and results[r.case_id].ok
                and results[r.case_id].mae is not None]
        med = f" · mediana MAE {np.median(maes):.3f}" if maes else ""
        cards: List[str] = []
        for r in items:
            res = results.get(r.case_id)
            link = f'<a href="reports/{r.case_id}.html">{r.case_id}</a>'
            if not (res and res.ok and res.cycles):
                err = _esc.escape((res.error if res else None)
                                  or "nunca simulado — rode o CLI --all")
                cards.append(f'<div class="pcard"><h3>{link}</h3>'
                             f'<p class="sub2">{err}</p></div>')
                continue
            series = []
            dx, dy = _data_points(r)
            if len(dx):
                ddx, ddy = _dec_xy(dx, dy)
                series.append(dict(name="dado", color="var(--pt)",
                                   x=ddx, y=ddy, points=True, line=True))
            # mesma convencao da pagina por caso: plotar o modelo ALINHADO,
            # que e' o que o MAE exibido ao lado mede (defeito 2026-07-27).
            amx, amy, _al = _aligned_model_xy(res, res.cycles, res.ratio)
            mx, my = _dec_xy(amx, amy)
            series.append(dict(name="modelo", color="var(--di)",
                               x=mx, y=my, line=True))
            met = (f'MAE {res.mae:.3f}' if res.mae is not None else 'MAE —')
            if res.resid_std is not None:
                met += f' · σ_res {res.resid_std:.3f}'
            if res.maxerr is not None:
                # meta permanente (professor 2026-07-14): residuo assinado
                # |modelo-artigo| < 0.1 em TODOS os pontos de cada curva
                cls = ' style="color:var(--warn)"' if res.maxerr > 0.10 else ''
                met += (f' · <span{cls}>|res|máx {res.maxerr:.3f}</span>')
            cards.append(
                f'<div class="pcard" data-href="reports/{r.case_id}.html" '
                f'title="clique no gráfico: report completo (condições, '
                f'modelo MSD, decomposição, constantes)">'
                f'<h3>{link} <span class="c">{met}</span></h3>'
                + _chart_div(dict(type="lines", h=150, xlabel="ciclo",
                                  ylabel="F/F0", name=r.case_id,
                                  series=series)) + '</div>')
        body.append(f'<h2>{NICE.get(src, src)} <span class="c">'
                    f'({len(items)} casos{med})</span></h2>'
                    f'<div class="plotgrid">{"".join(cards)}</div>')
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Todos os gráficos — dado × modelo</title>{_CSS}
<style>.plotgrid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(420px,1fr));
 gap:10px;margin:6px 0 14px}}.pcard{{background:var(--card);border:1px solid var(--bd);
 border-radius:8px;padding:8px 10px;min-width:0}}.pcard h3{{margin:0 0 4px;font-size:.8rem;
 font-family:Consolas,monospace;overflow-wrap:anywhere}}.pcard h3 a{{color:var(--accent);
 text-decoration:none}}.pcard .c{{color:var(--mut);font-weight:400;font-size:.72rem}}
.pcard[data-href] .chart{{cursor:pointer}}
.pcard[data-href]:hover{{border-color:var(--accent)}}
h2 .c{{font-size:.72rem;color:var(--mut);text-transform:none;letter-spacing:0}}</style>
</head><body>{_topbar("Todos os gráficos — dado × modelo",
                      f'<span class="chip"><a href="validation_report.html" '
                      f'style="color:inherit">← mestre</a></span>')}<div class="wrap">
<h1>Todos os gráficos — dado × modelo (store canônico)</h1>
<p class="sub"><b>Clique em qualquer gráfico para abrir o report completo do
 caso</b> — condições de contorno com proveniência, <b>modelo MSD usado</b>
 (cadeia de elementos, k/c/m, carregamento), decomposição por mecanismo e
 constantes. Curvas aqui decimadas a ≤220 pontos; a legenda continua
 clicável (liga/desliga série) e o arrasto dá zoom — só o clique parado
 navega.</p>
{"".join(body)}
<p class="foot">Gerado por bolt_analysis_studio.validation.report_html
 (all_plots_html) do validation_store canônico.</p>
</div>{_CHART_JS}<script>
/* clique parado no grafico -> report completo do caso (pedido 2026-07-14).
   Guard de 6px preserva o zoom por arrasto do BASCHART; legenda/CSV vivem
   fora do div .chart, entao nao sao afetados. */
document.querySelectorAll('.pcard[data-href]').forEach(function(card){{
 var area=card.querySelector('.chart');if(!area)return;
 var sx=0,sy=0;
 area.addEventListener('pointerdown',function(ev){{sx=ev.clientX;sy=ev.clientY;}});
 area.addEventListener('pointerup',function(ev){{
  if(Math.hypot(ev.clientX-sx,ev.clientY-sy)<6)
   window.location.href=card.dataset.href;}});
}});
</script></body></html>'''


def write_reports(out_dir: Optional[Path] = None,
                  results: Optional[Dict[str, Optional[CaseResult]]] = None,
                  store_path: Optional[Path] = None) -> Path:
    """Escreve reports/<case_id>.html p/ TODOS os records + validation_report.html.
    `results` default = ValidationStore em `store_path` (com seed da galeria
    se vazio)."""
    out = Path(out_dir) if out_dir else repo_root() / "New_Theory" / "validation_html"
    rep = out / "reports"
    rep.mkdir(parents=True, exist_ok=True)
    records = all_records()
    if results is None:
        from .store import ValidationStore
        store = ValidationStore(path=store_path)
        if not store.all_ids():
            store.seed_from_gallery()
            store.save()
        results = {r.case_id: store.get(r.case_id) for r in records}
    full: Dict[str, CaseResult] = {}
    for r in records:
        res = results.get(r.case_id)
        if res is None:
            res = CaseResult(case_id=r.case_id, ok=False,
                             error="nunca simulado — rode o CLI --all",
                             generated_at="—", engine_fingerprint="—")
        full[r.case_id] = res
    # D1: os pisos são medidos UMA vez sobre o conjunto e o limite efetivo da
    # fonte desce para cada página de caso — a página e o mestre julgam pela
    # MESMA régua. Com a flag desligada `limite_sres` devolve o global e o
    # argumento vira inócuo (`_tripe_block` trata None e global igual).
    _pis = (_pisos_medidos([(r.source, full[r.case_id]) for r in records])
            if _SRES_POR_FONTE else None)
    # Fonte retirada não ganha página, e a página que existir é REMOVIDA. Só
    # deixar de escrever não basta: o arquivo antigo continuaria no disco (e no
    # git) servindo uma página que o documento não linka mais — um relatório de
    # validação órfão é pior que nenhum, porque ainda abre, ainda parece oficial
    # e ninguém mais o vê para notar que envelheceu.
    for r in records:
        alvo = rep / f"{r.case_id}.html"
        if not caso_no_documento(r.source, r.case_id):
            if alvo.exists():
                alvo.unlink()
            continue
        alvo.write_text(
            case_report_html(r, full[r.case_id],
                             lim_sd=limite_sres(r.source, _pis)),
            encoding="utf-8")
    master = out / "validation_report.html"
    master.write_text(master_report_html(records, full), encoding="utf-8")
    (out / "all_plots.html").write_text(all_plots_html(records, full),
                                        encoding="utf-8")
    return master


_CSS = """<style>
:root{--bg:#faf9f7;--fg:#1c1a17;--mut:#6b655c;--card:#fff;--bd:#e6e1d8;--di:#2f6f8f;
 --err:#c0392b;--pt:#1c1a17;--good:#1a7a4c;--warn:#b3452c;--accent:#8a6a00}
@media(prefers-color-scheme:dark){:root{--bg:#16140f;--fg:#ece7de;--mut:#9a938a;--card:#211e18;
 --bd:#332e26;--di:#6bb6d6;--err:#e8776b;--pt:#ece7de;--good:#5fd39a;--warn:#e8936b;--accent:#f2c744}}
:root[data-theme=dark]{--bg:#16140f;--fg:#ece7de;--mut:#9a938a;--card:#211e18;--bd:#332e26;
 --di:#6bb6d6;--err:#e8776b;--pt:#ece7de;--good:#5fd39a;--warn:#e8936b;--accent:#f2c744}
:root[data-theme=light]{--bg:#faf9f7;--fg:#1c1a17;--mut:#6b655c;--card:#fff;--bd:#e6e1d8;
 --di:#2f6f8f;--err:#c0392b;--pt:#1c1a17;--good:#1a7a4c;--warn:#b3452c;--accent:#8a6a00}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);
 font:15px/1.55 -apple-system,"Segoe UI",Roboto,sans-serif;padding:24px 20px 60px}
.wrap{max-width:1000px;margin:0 auto}
a,a:visited{color:var(--accent)}   /* sem isto, link sem regra cai no azul do navegador */
.back{font-size:.8rem;margin:0 0 8px}.back a{color:var(--accent);text-decoration:none}
h1{font-size:1.4rem;margin:0 0 2px;font-family:Consolas,monospace}
.sub{color:var(--mut);margin:0 0 18px;font-size:.9rem}.sub a{color:var(--accent)}
.sub2{color:var(--mut);font-size:.78rem;margin:2px 0 8px;font-family:Consolas,monospace}
h2{font-size:.95rem;text-transform:uppercase;letter-spacing:.05em;color:var(--accent);
 margin:20px 0 8px;border-bottom:1px solid var(--bd);padding-bottom:4px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:22px}
/* recorte da figura do artigo na conferencia da digitalizacao (2026-07-29) */
.pfig{margin:0 0 10px}
/* veredicto do tripé por perna (§3). Borda no --accent porque é a MESMA leitura
   que o gradiente do 3D do documento mestre carrega, e o leitor tem de
   reconhecê-la de um lugar no outro. */
.tripe{border:1px solid var(--bd);border-left:3px solid var(--accent);
 border-radius:8px;padding:8px 12px;margin:10px 0}
.tripe h3,.tripe h4{margin:2px 0 4px}
.tripe h4{font-size:.86rem;color:var(--mut)}
.tripe td:nth-child(2),.tripe td:nth-child(3){font-variant-numeric:tabular-nums;
 text-align:right}
.tripe td.good{color:var(--good)}.tripe td.warn{color:var(--warn)}
.pfig img{width:100%;height:auto;border:1px solid var(--bd);border-radius:6px;
 background:#fff}
.pfig figcaption{font-size:.74rem;color:var(--mut);margin-top:3px;
 font-family:Consolas,monospace}
@media(max-width:760px){.grid2{grid-template-columns:1fr}}
table{border-collapse:collapse;width:100%;font-size:.82rem}
table.wide{font-size:.8rem}
td{padding:4px 8px;border-bottom:1px solid var(--bd);vertical-align:top}
td.k{color:var(--mut);white-space:nowrap;width:42%}td.v{font-family:Consolas,monospace}
.pv{font-size:.72rem;color:var(--mut)}
.metric{font-size:1.7rem;font-weight:750;font-family:Consolas,monospace}
.metric.good{color:var(--good)}.metric.warn{color:var(--warn)}
.plot{width:100%;height:auto;display:block;margin:6px 0}
.gl{stroke:var(--bd);stroke-width:.6}.tk{fill:var(--mut);font-size:9px}.axl{fill:var(--mut);font-size:10px}
.err{stroke:var(--err);stroke-width:2.2;opacity:.5}.ml{stroke:var(--di);stroke-width:2.2}.pt{fill:var(--pt)}
.lg{font-size:.72rem;color:var(--mut);margin-top:2px}
.lg .s{display:inline-block;width:16px;height:8px;vertical-align:middle;margin:0 3px}
.lg .s.ml{background:var(--di)}.lg .s.pt{background:var(--pt);border-radius:50%;width:8px}
.lg .s.err{background:var(--err);opacity:.5}
.verd{font-size:.82rem;color:var(--fg);background:var(--card);border:1px solid var(--bd);
 border-left:3px solid var(--accent);border-radius:8px;padding:10px 14px;max-width:90ch}
.band{fill:var(--accent);opacity:.12}.zl{stroke:var(--fg);stroke-width:.8}
.trimz{fill:var(--err);opacity:.07}.triml{stroke:var(--err);stroke-width:1;
 stroke-dasharray:4,3;opacity:.7}
.rl{stroke:var(--err);stroke-width:2}.narr{font-size:.85rem;max-width:75ch}
.lg .s.rl{background:var(--err)}.lg .s.band{background:var(--accent);opacity:.25}
.box{fill:var(--card);stroke:var(--accent);stroke-width:1.2}
.box.ground{stroke:var(--mut);stroke-dasharray:4 3}
.bt{fill:var(--fg);font-size:10px;font-family:Consolas,monospace}
.cn{stroke:var(--accent);stroke-width:1.5}.ovx{overflow-x:auto}
.steps{font-size:.85rem;max-width:80ch}
h3{font-size:.85rem;color:var(--fg);margin:12px 0 4px}
th{text-align:left;color:var(--mut);font-weight:600;font-size:.72rem;
 padding:4px 8px;border-bottom:1px solid var(--bd)}
svg.chain{max-width:560px}
.foot{font-size:.72rem;color:var(--mut);margin-top:22px;border-top:1px solid var(--bd);padding-top:10px}
.exec{font-size:.9rem;margin:0 0 16px}.exec .metric{font-size:1.15rem}
body{padding-top:58px}
.topbar{position:fixed;top:0;left:0;right:0;background:var(--card);
 border-bottom:1px solid var(--bd);padding:7px 16px;display:flex;gap:12px;
 align-items:center;z-index:10}
.tb-title{font-family:Consolas,monospace;font-weight:700;font-size:.9rem}
.tb-right{margin-left:auto;display:flex;gap:8px}
.topbar button{background:var(--bg);color:var(--mut);border:1px solid var(--bd);
 border-radius:999px;padding:4px 12px;font:inherit;font-size:.72rem;cursor:pointer}
.topbar button:hover{color:var(--fg);border-color:var(--accent)}
.toc{position:fixed;left:14px;top:76px;width:195px;font-size:.78rem;
 line-height:2;display:none}
.toc b{color:var(--mut);text-transform:uppercase;font-size:.68rem;letter-spacing:.06em}
.toc a{display:block;color:var(--mut);text-decoration:none;border-left:2px solid var(--bd);
 padding-left:8px}.toc a:hover{color:var(--fg)}
.toc a.on{color:var(--accent);font-weight:700;border-left-color:var(--accent)}
@media(min-width:1400px){.toc{display:block}}
.chart-box{position:relative}
.ctip{position:absolute;background:var(--card);border:1px solid var(--bd);
 border-radius:6px;padding:6px 9px;font:11px Consolas,monospace;line-height:1.6;
 pointer-events:none;z-index:5;box-shadow:0 2px 8px rgba(0,0,0,.25);max-width:220px}
.cbar{display:flex;flex-wrap:wrap;gap:10px;align-items:center;font-size:.72rem;
 color:var(--mut);margin:2px 0 10px}
.citem{cursor:pointer;user-select:none}
.citem.off{opacity:.35;text-decoration:line-through}
.citem .sw{display:inline-block;width:12px;height:8px;margin-right:4px;border-radius:2px}
.cbtn{background:var(--card);color:var(--mut);border:1px solid var(--bd);
 border-radius:6px;padding:3px 10px;font:inherit;font-size:.72rem;cursor:pointer}
.cbtn:hover{color:var(--fg);border-color:var(--accent)}
.chint{font-size:.68rem;opacity:.8}
h2.collapsible{cursor:pointer}
h2.collapsible::after{content:" ▾";color:var(--mut)}
h2.collapsible.closed::after{content:" ▸"}
.chips{margin:0 0 10px}
.chip{display:inline-block;background:var(--card);border:1px solid var(--bd);
 border-radius:999px;padding:4px 12px;margin:0 6px 8px 0;font-size:.78rem}
.chip b{font-family:Consolas,monospace}
#filtro{width:100%;max-width:420px;background:var(--card);color:var(--fg);
 border:1px solid var(--bd);border-radius:8px;padding:7px 12px;font:inherit}
@media print{body{background:#fff;color:#111;padding:0}
 .plot,table,svg,.chart-box{break-inside:avoid}
 .back,.topbar,.toc,.cbar,#filtro{display:none}
 .secbody{display:block!important}
 .grid2{display:block}}
</style>"""
