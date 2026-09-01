# -*- coding: utf-8 -*-
"""Reconstrói concept_not-a-fit.html no VISUAL DO TUTORIAL DE USO e ENRIQUECE a
prova "não é um fit": 4 overlays interativos (mais variáveis que só amplitude, e
exemplos AXIAL + CISALHANTE), cada um confrontando o MODELO (uma única config
física, zero-refit) com o DADO real e com uma INTERPOLAÇÃO ajustada a UMA condição
(que erra fora dela). Dados = store canônico de validação.

    python New_Theory/build_variable_explorer.py    # gera a página base
    python New_Theory/restyle_notafit.py            # reestiliza + enriquece

Idempotente: extrai os painéis de prosa por contagem de <div> e reconstrói os
overlays do store a cada rodada.
"""
import json
import pathlib
import re
import sys

sys.path.insert(0, "src")
sys.path.insert(0, "New_Theory")
from build_variable_explorer import _validation_cases  # noqa: E402

P = pathlib.Path("New_Theory/variable_explorer/concept_not-a-fit.html")
src = P.read_text(encoding="utf-8")

CASES = {c["cid"]: c for c in _validation_cases()}


def _num(cid, suf, pre=""):
    m = re.search(pre + r"([0-9p]+)" + suf, cid)
    return m.group(1).replace("p", ".") if m else "?"


def _interp_fn(ref):
    """Interpolação = a FORMA do caso de referência (normalizada em N), aplicada
    SEM MUDAR. Sabe reproduzir a condição em que foi ajustada; não sabe física."""
    if not ref or not ref["data_N"] or ref["data_N"][-1] <= 0:
        return lambda t: 1.0
    nend = float(ref["data_N"][-1])
    fr = [n / nend for n in ref["data_N"]]
    rr = list(ref["data_r"])

    def f(t):
        t = min(1.0, max(0.0, t))
        for k in range(1, len(fr)):
            if fr[k] >= t:
                f0, f1 = fr[k - 1], fr[k]
                w = (t - f0) / (f1 - f0) if f1 > f0 else 0.0
                return rr[k - 1] + w * (rr[k] - rr[k - 1])
        return rr[-1]
    return f


def build_series(cids, ref_cid, label):
    ref = CASES.get(ref_cid)
    ip = _interp_fn(ref)
    out = []
    for cid in cids:
        c = CASES.get(cid)
        if not c:
            continue
        mend = float(c["model_N"][-1]) or 1.0
        interp_r = [round(ip(n / mend), 4) for n in c["model_N"]]
        dend = float(c["data_N"][-1]) or 1.0
        ie = [abs(ip(dn / dend) - dr) for dn, dr in zip(c["data_N"], c["data_r"])]
        imae = round(sum(ie) / len(ie), 4) if ie else 0.0
        out.append({"label": label(c, cid),
                    "model_N": c["model_N"], "model_r": c["model_r"],
                    "data_N": c["data_N"], "data_r": c["data_r"],
                    "interp_r": interp_r, "interp_mae": imae, "mae": c["mae"]})
    return out


OVERLAYS = [
    dict(id="amp_shear", pt="Amplitude · cisalhante", en="Amplitude · shear",
         rig="Liu 2025 — M16 8.8, F0 60 kN, 12.5 Hz",
         cids=["liu2025_M16_amp0p25", "liu2025_M16_amp0p3", "liu2025_M16_amp0p4",
               "liu2025_M16_amp0p5", "liu2025_M16_amp0p6", "liu2025_M16_amp0p8"],
         ref="liu2025_M16_amp0p25", ref_pt="±0,25 mm", ref_en="0.25 mm",
         label=lambda c, cid: "±%.2f mm" % c["amp_mm"]),
    dict(id="amp_axial", pt="Amplitude axial (A_F) · axial", en="Axial amplitude (A_F) · axial",
         rig="Liu 2017 — M12, 30 Hz, excitação axial",
         cids=["liu2017_axial_AF_7p5kN", "liu2017_axial_AF_8p75kN",
               "liu2017_axial_AF_11p25kN", "liu2017_axial_AF_12p5kN"],
         ref="liu2017_axial_AF_7p5kN", ref_pt="A_F = 7,5 kN", ref_en="A_F = 7.5 kN",
         label=lambda c, cid: "A_F = %s kN" % _num(cid, "kN", "AF_")),
    dict(id="preload_axial", pt="Pré-carga F0 · axial", en="Preload F0 · axial",
         rig="Liu 2017 — M12, 30 Hz, excitação axial",
         cids=["liu2017_axial_F0_15kN", "liu2017_axial_F0_16p5kN", "liu2017_axial_F0_18kN",
               "liu2017_axial_F0_19p5kN", "liu2017_axial_F0_21kN"],
         ref="liu2017_axial_F0_15kN", ref_pt="F0 = 15 kN", ref_en="F0 = 15 kN",
         label=lambda c, cid: "F0 = %s kN" % _num(cid, "kN", "F0_")),
    dict(id="freq_axial", pt="Frequência · axial", en="Frequency · axial",
         rig="Li 2022 — Ti, excitação axial",
         cids=["li2022ti_axialmin_10Hz", "li2022ti_axialmin_15Hz", "li2022ti_axialmin_20Hz"],
         ref="li2022ti_axialmin_10Hz", ref_pt="10 Hz", ref_en="10 Hz",
         label=lambda c, cid: "%s Hz" % _num(cid, "Hz")),
]

# --- painéis de prosa preservados (extraídos por contagem de <div>) ---


def first_div(html, marker, frm=0):
    start = html.index(marker, frm)
    depth = 0
    for m in re.finditer(r"<div\b|</div>", html[start:]):
        depth += -1 if m.group() == "</div>" else 1
        if depth == 0:
            return html[start:start + m.end()], start + m.end()
    return html[start:], len(html)


panels = []
pos = 0
while True:
    try:
        idx = src.index('<div class="panel">', pos)
    except ValueError:
        break
    blk, pos = first_div(src, '<div class="panel">', idx)
    panels.append(blk)
prose = "\n".join(panels)

# --- monta os overlays (HTML + <script> de dados) ---
ov_html, ov_scripts, toc_ov = [], [], []
built = 0
for ov in OVERLAYS:
    series = build_series(ov["cids"], ov["ref"], ov["label"])
    if not series:
        continue
    built += 1
    last = len(series) - 1
    opts = "".join('<option value="%d"%s>%s</option>'
                   % (i, " selected" if i == last else "", s["label"])
                   for i, s in enumerate(series))
    ov_html.append(
        '<div class="ovl reveal" id="ov-%s" data-ov="%s">' % (ov["id"], ov["id"])
        + '<div class="ovl-head"><b>%s</b><span data-l="pt"> · %s</span>'
          '<span data-l="en"> · %s</span></div>' % (ov["pt"].split(" · ")[0], ov["rig"], ov["rig"])
        + '<canvas></canvas>'
        + '<div class="ovl-ctl"><label><span data-l="pt">condição</span>'
          '<span data-l="en">condition</span>&nbsp;<select>' + opts + "</select></label>"
        + '<span class="ovl-read"></span></div>'
        + '<div class="ovl-legend">'
          '<span style="color:var(--accent)">&#9473; <span data-l="pt">modelo (previsão, uma física)</span>'
          '<span data-l="en">model (prediction, one physics)</span></span> &nbsp;·&nbsp; '
          '<span style="color:var(--muted)">&#183;&#183;&#183; <span data-l="pt">interpolação (ajustada em %s)</span>'
          '<span data-l="en">interpolation (fitted at %s)</span></span> &nbsp;·&nbsp; '
          '<span style="color:var(--warn)">&#9679; <span data-l="pt">dado medido</span>'
          '<span data-l="en">measured data</span></span></div>' % (ov["ref_pt"], ov["ref_en"])
        + "</div>")
    ov_scripts.append(
        "<script>window.OVL=window.OVL||{};window.OVL['%s']=%s;</script>"
        % (ov["id"], json.dumps({"series": series, "start": last})))
    toc_ov.append('<a href="#ov-%s"><span data-l="pt">%s</span><span data-l="en">%s</span></a>'
                  % (ov["id"], ov["pt"], ov["en"]))

CSS = r"""
:root{
  --bg:#15161b; --bg2:#1a1b22; --panel:#1e1f27; --panel2:#262832;
  --ink:#cdd6f4; --muted:#a6adc8; --line:#313244; --line2:#3a3d4d;
  --accent:#4aa3e0; --accent2:#f0868b; --ghost:#454a5a; --code-bg:#232530;
  --ok:#a6e3a1; --warn:#e5c07b; --side:#1a1b22; --side-w:272px;
  --disp:'Bahnschrift','DIN Alternate','Segoe UI',system-ui,sans-serif;
  --body:'Segoe UI',system-ui,-apple-system,sans-serif;
  --mono:'Consolas','Cascadia Code',monospace;
}
*{box-sizing:border-box} html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--body);font-size:15px;line-height:1.6}
a{color:var(--accent);text-decoration:none} a:hover{text-decoration:underline}
code{font-family:var(--mono);background:var(--code-bg);border:1px solid var(--line);border-radius:4px;padding:.05em .35em;font-size:.88em;color:#dfe6f5}
[data-lang="pt"] [data-l="en"]{display:none}
[data-lang="en"] [data-l="pt"]{display:none}
.wrap{display:grid;grid-template-columns:var(--side-w) minmax(0,1fr);max-width:1520px;margin:0 auto}
nav.toc{position:sticky;top:0;align-self:start;height:100vh;overflow-y:auto;padding:22px 15px 44px;border-right:1px solid var(--line);background:var(--side)}
nav.toc .brand{font-family:var(--disp);font-weight:700;letter-spacing:.4px;font-size:15px;color:#fff;line-height:1.2}
nav.toc .brand span{display:block;font-size:10.5px;font-weight:600;color:var(--accent);letter-spacing:1.4px;margin-top:3px}
nav.toc .lang{display:flex;gap:6px;margin:14px 4px 4px}
nav.toc .lang button{flex:1;background:var(--panel);border:1px solid var(--line);color:var(--muted);border-radius:7px;padding:5px;font-size:12px;cursor:pointer;font-family:var(--mono);transition:all .15s}
nav.toc .lang button.on{background:var(--accent);color:#08121c;border-color:var(--accent);font-weight:700}
nav.toc .sep{margin:16px 6px 6px;font-size:10.5px;letter-spacing:1.4px;text-transform:uppercase;color:var(--muted)}
nav.toc a{display:block;color:var(--muted);padding:5px 9px;border-radius:6px;font-size:13px;border-left:2px solid transparent;transition:transform .15s ease,background .15s,color .15s}
nav.toc a:hover{background:var(--panel);color:var(--ink);text-decoration:none;transform:translateX(2px)}
nav.toc a.active{background:var(--panel);color:#fff;border-left-color:var(--accent)}
main{padding:0 clamp(18px,3.5vw,54px) 90px;min-width:0}
header.hero{margin:0 calc(-1*clamp(18px,3.5vw,54px)) 26px;padding:58px clamp(18px,3.5vw,54px) 34px;border-bottom:1px solid var(--line);position:relative;overflow:hidden;
  background:radial-gradient(1100px 320px at 18% -20%, #24344d66, transparent),radial-gradient(820px 300px at 92% -10%, #2c2140aa, transparent), var(--bg2)}
header.hero::before{content:"";position:absolute;inset:0;pointer-events:none;background-image:linear-gradient(var(--line) 1px,transparent 1px),linear-gradient(90deg,var(--line) 1px,transparent 1px);background-size:34px 34px;opacity:.09}
header.hero>*{position:relative}
header.hero .kicker{font-family:var(--mono);font-size:12px;letter-spacing:3px;text-transform:uppercase;color:var(--accent)}
header.hero h1{font-family:var(--disp);font-weight:700;letter-spacing:.4px;font-size:clamp(28px,4.4vw,46px);margin:8px 0 10px;color:#fff;line-height:1.03}
header.hero p.lead{max-width:72ch;color:var(--muted);font-size:15.5px;margin:0}
h2.sec{font-family:var(--disp);font-weight:700;font-size:19px;color:#fff;margin:0 0 .6rem;letter-spacing:.02em}
.secband{font-family:var(--disp);font-weight:700;font-size:22px;color:#fff;margin:30px 0 6px;padding-bottom:6px;border-bottom:1px solid var(--line)}
.intro{color:var(--muted);max-width:76ch;margin:8px 0 6px}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:18px 20px;margin:18px 0}
.panel p{margin:.5rem 0}
ul.refs{margin:.3rem 0 0;padding-left:1.15rem}
ul.refs li{margin:.4rem 0;font-size:.94rem}
ul.refs li.refhead{list-style:none;margin:14px 0 4px -1.15rem;color:var(--muted);font-size:.72rem;text-transform:uppercase;letter-spacing:.06em;font-weight:700}
ul.refs .src{color:var(--muted);font-size:.85rem}
.note{background:var(--code-bg);border-left:3px solid var(--warn);padding:10px 14px;border-radius:0 8px 8px 0;font-size:.9rem;color:var(--muted);margin:.8rem 0}
.related a{display:inline-block;margin-right:10px;font-family:var(--mono);font-size:.85rem}
nav.pn{display:flex;justify-content:space-between;margin-top:26px;font-size:.9rem;gap:10px;flex-wrap:wrap}
/* overlays */
.ovl{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:14px 16px;margin:16px 0}
.ovl-head{font-size:.9rem;color:var(--muted);margin-bottom:8px}
.ovl-head b{color:#fff;font-family:var(--disp);font-size:1.05rem}
.ovl canvas{width:100%;height:auto;display:block;cursor:crosshair}
.ovl-ctl{display:flex;align-items:center;gap:16px;flex-wrap:wrap;margin-top:10px}
.ovl-ctl select{background:var(--code-bg);color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:6px 10px;font-family:var(--mono);cursor:pointer}
.ovl-read{font-family:var(--mono);font-size:.95rem}
.ovl-legend{font-size:.78rem;color:var(--muted);margin-top:9px}
.ovl-cap{font-size:.86rem;color:var(--muted);margin-top:8px;line-height:1.5}
footer{color:var(--muted);font-size:12.5px;padding:34px 0 0;border-top:1px solid var(--line);margin-top:30px;line-height:1.7}
/* animações */
@keyframes ve-rise{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:none}}
.gprog{position:fixed;top:0;left:0;height:3px;width:0;z-index:100;background:linear-gradient(90deg,var(--accent),#cba6f7);box-shadow:0 0 10px var(--accent);transition:width .08s linear}
.reveal{opacity:0;transform:translateY(18px)}
.reveal.in{opacity:1;transform:none;transition:opacity .6s cubic-bezier(.2,.7,.2,1),transform .6s cubic-bezier(.2,.7,.2,1)}
header.hero .kicker{animation:ve-rise .7s cubic-bezier(.2,.7,.2,1) both}
header.hero h1{animation:ve-rise .7s .08s cubic-bezier(.2,.7,.2,1) both}
header.hero p.lead{animation:ve-rise .7s .16s cubic-bezier(.2,.7,.2,1) both}
@media(max-width:900px){.wrap{grid-template-columns:1fr}nav.toc{position:static;height:auto;border-right:0;border-bottom:1px solid var(--line)}}
@media(prefers-reduced-motion:reduce){.reveal,.reveal.in{opacity:1!important;transform:none!important;transition:none!important}header.hero .kicker,header.hero h1,header.hero p.lead{animation:none}.gprog{display:none}nav.toc a:hover{transform:none}}
"""

OVL_JS = r"""
window.OVL=window.OVL||{};
(function(){
  var root=document.documentElement, cs=getComputedStyle(root), col=function(n){return cs.getPropertyValue(n).trim();};
  function f3(x){return (Math.round(x*1000)/1000).toFixed(3);}
  function draw(host){
    var d=window.OVL[host.getAttribute('data-ov')]; if(!d)return;
    var cv=host.querySelector('canvas'), ctx=cv.getContext('2d');
    var sel=host.querySelector('select'), idx=sel?+sel.value:(d.start||0);
    var s=d.series[idx]; if(!s)return;
    var w=cv.clientWidth||760,h=Math.round(w*0.5),dpr=window.devicePixelRatio||1;
    cv.width=w*dpr;cv.height=h*dpr;cv.style.height=h+'px';ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,w,h);
    var PAD={l:52,r:12,t:12,b:34};
    var xmax=Math.max(1,s.model_N[s.model_N.length-1],s.data_N[s.data_N.length-1]);
    var y0=1,y1=0,i;
    for(i=0;i<s.model_r.length;i++){if(s.model_r[i]<y0)y0=s.model_r[i];if(s.model_r[i]>y1)y1=s.model_r[i];}
    for(i=0;i<s.data_r.length;i++){if(s.data_r[i]<y0)y0=s.data_r[i];if(s.data_r[i]>y1)y1=s.data_r[i];}
    for(i=0;i<s.interp_r.length;i++){if(s.interp_r[i]<y0)y0=s.interp_r[i];if(s.interp_r[i]>y1)y1=s.interp_r[i];}
    if(y1<=y0){y0=0;y1=1;} var pd=(y1-y0)*0.08||0.02; y0=Math.max(0,y0-pd);y1=Math.min(1.02,y1+pd);
    var X=function(n){return PAD.l+(n/xmax)*(w-PAD.l-PAD.r);};
    var Y=function(r){var rr=Math.max(y0,Math.min(y1,r));return PAD.t+(1-(rr-y0)/(y1-y0))*(h-PAD.t-PAD.b);};
    ctx.strokeStyle=col('--line');ctx.fillStyle=col('--muted');ctx.font="11px 'Segoe UI',sans-serif";ctx.lineWidth=1;
    ctx.textAlign='right';ctx.textBaseline='middle';
    for(var g=0;g<=4;g++){var v=y1-(g/4)*(y1-y0),y=PAD.t+(g/4)*(h-PAD.t-PAD.b);ctx.globalAlpha=.5;ctx.beginPath();ctx.moveTo(PAD.l,y);ctx.lineTo(w-PAD.r,y);ctx.stroke();ctx.globalAlpha=1;ctx.fillText(v.toFixed(2),PAD.l-6,y);}
    ctx.textAlign='center';ctx.textBaseline='top';for(var g2=0;g2<=4;g2++){var nn=Math.round(xmax*g2/4);ctx.fillText(nn,X(nn),h-PAD.b+6);}
    ctx.save();ctx.translate(12,h/2);ctx.rotate(-Math.PI/2);ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText('F / F0',0,0);ctx.restore();
    ctx.textAlign='center';ctx.fillText(root.dataset.lang==='en'?'cycle':'ciclo',(PAD.l+w-PAD.r)/2,h-13);
    ctx.strokeStyle=col('--muted');ctx.lineWidth=1.6;ctx.setLineDash([6,4]);ctx.beginPath();
    for(i=0;i<s.model_N.length;i++){var xa=X(s.model_N[i]),ya=Y(s.interp_r[i]);i?ctx.lineTo(xa,ya):ctx.moveTo(xa,ya);}ctx.stroke();ctx.setLineDash([]);
    ctx.strokeStyle=col('--accent');ctx.lineWidth=2.8;ctx.beginPath();
    for(i=0;i<s.model_N.length;i++){var xb=X(s.model_N[i]),yb=Y(s.model_r[i]);i?ctx.lineTo(xb,yb):ctx.moveTo(xb,yb);}ctx.stroke();
    ctx.fillStyle=col('--warn');
    for(i=0;i<s.data_N.length;i++){ctx.beginPath();ctx.arc(X(s.data_N[i]),Y(s.data_r[i]),3,0,6.2832);ctx.fill();}
    var ro=host.querySelector('.ovl-read'); if(ro){var pt=root.dataset.lang!=='en';
      ro.innerHTML='<b style="color:'+col('--accent')+'">'+(pt?'MAE modelo ':'model MAE ')+f3(s.mae)+'</b> &nbsp;·&nbsp; '
        +'<span style="color:'+col('--muted')+'">'+(pt?'MAE interpolação ':'interp MAE ')+f3(s.interp_mae)+'</span>';}
  }
  window._ovlAll=function(){document.querySelectorAll('.ovl').forEach(draw);};
  document.querySelectorAll('.ovl').forEach(function(host){
    var sel=host.querySelector('select'); if(sel)sel.addEventListener('change',function(){draw(host);}); draw(host);});
  window.addEventListener('resize',window._ovlAll);
})();
"""

SHELL_JS = r"""
(function(){
  var reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
  window.setLang=function(l){document.documentElement.dataset.lang=l;
    document.querySelectorAll('nav.toc .lang button').forEach(function(b){b.classList.toggle('on',b.getAttribute('data-l')===l);});
    if(window._ovlAll)window._ovlAll();};
  setLang(document.documentElement.dataset.lang||'pt');
  if(!reduce){
    var bar=document.createElement('div');bar.className='gprog';document.body.appendChild(bar);
    function pg(){var hh=document.documentElement.scrollHeight-innerHeight;bar.style.width=(hh>0?scrollY/hh*100:0)+'%';}
    addEventListener('scroll',pg,{passive:true});addEventListener('resize',pg);pg();
    var vh=innerHeight||800;
    var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target);}});},{rootMargin:'0px 0px -6% 0px'});
    document.querySelectorAll('.panel,.ovl,.secband').forEach(function(el){if(el.getBoundingClientRect().top>vh*0.9){el.classList.add('reveal');io.observe(el);}});
  }
  var links={};document.querySelectorAll('nav.toc a[href^="#"]').forEach(function(a){links[a.getAttribute('href').slice(1)]=a;});
  var aio=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){var a=links[e.target.id];
    if(a){for(var k in links)links[k].classList.remove('active');a.classList.add('active');}}});},{rootMargin:'-35% 0px -58% 0px'});
  Object.keys(links).forEach(function(id){var el=document.getElementById(id);if(el)aio.observe(el);});
})();
"""

hero = (
    '<header class="hero">'
    '<div class="kicker"><span data-l="pt">Fundamentos · não é um fit</span>'
    '<span data-l="en">Foundations · not a fit</span></div>'
    '<h1><span data-l="pt">Isto não é um ajuste de curva</span>'
    '<span data-l="en">This is not a curve fit</span></h1>'
    '<p class="lead"><span data-l="pt">Uma <b>única configuração física</b> (mesmas constantes, '
    'zero-refit) prevê o afrouxamento ao variar a <b>amplitude</b>, a <b>pré-carga</b> e a '
    '<b>frequência</b>, em carregamento <b>cisalhante</b> e <b>axial</b>. Uma interpolação ajustada '
    'a UMA condição acerta só ali e erra fora dela — troque a condição em cada gráfico e compare o '
    'MAE.</span><span data-l="en">A <b>single physical configuration</b> (same constants, zero-refit) '
    'predicts loosening as <b>amplitude</b>, <b>preload</b> and <b>frequency</b> change, under '
    '<b>shear</b> and <b>axial</b> loading. An interpolation fitted to ONE condition is right only '
    'there and drifts elsewhere — switch the condition in each plot and compare the MAE.</span></p>'
    '</header>')

sidebar = (
    '<nav class="toc">'
    '<div class="brand">Bolt Analysis Studio<span>V2 · NÃO É UM FIT</span></div>'
    '<div class="lang"><button data-l="pt" onclick="setLang(\'pt\')">PT</button>'
    '<button data-l="en" onclick="setLang(\'en\')">EN</button></div>'
    '<div class="sep"><span data-l="pt">Navegação</span><span data-l="en">Navigation</span></div>'
    '<a href="index.html">← <span data-l="pt">Explorador</span><span data-l="en">Explorer</span></a>'
    '<a href="concept_gallery.html"><span data-l="pt">Galeria de validação</span><span data-l="en">Validation gallery</span></a>'
    '<div class="sep"><span data-l="pt">A prova visual</span><span data-l="en">The visual proof</span></div>'
    + "".join(toc_ov) +
    '<div class="sep"><span data-l="pt">Leitura</span><span data-l="en">Reading</span></div>'
    '<a href="#prova"><span data-l="pt">O argumento</span><span data-l="en">The argument</span></a>'
    '</nav>')

prova_intro = (
    '<div class="secband" id="prova"><span data-l="pt">A prova visual — quatro varreduras</span>'
    '<span data-l="en">The visual proof — four sweeps</span></div>'
    '<p class="intro"><span data-l="pt">Em cada gráfico a <b>linha cheia</b> é o MODELO (a mesma '
    'física em todas as condições), os <b>pontos</b> são o dado medido, e a <b>linha tracejada</b> é '
    'uma interpolação ajustada a UMA condição e aplicada sem mudar. A interpolação acerta só onde foi '
    'ajustada; o modelo prevê todas. Note o MAE de cada um.</span>'
    '<span data-l="en">In each plot the <b>solid line</b> is the MODEL (the same physics across all '
    'conditions), the <b>dots</b> are measured data, and the <b>dashed line</b> is an interpolation '
    'fitted to ONE condition and applied unchanged. The interpolation is right only where it was '
    'fitted; the model predicts them all. Watch each MAE.</span></p>')

page = (
    "<!DOCTYPE html>\n"
    '<html lang="pt" data-lang="pt">\n<head>\n'
    '<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    "<title>Isto não é um fit — Bolt Analysis Studio V2</title>\n"
    "<style>" + CSS + "</style>\n</head>\n<body>\n"
    '<div class="wrap">\n' + sidebar + "\n<main>\n" + hero + "\n"
    + prova_intro + "\n" + "\n".join(ov_html) + "\n"
    + '<div class="secband"><span data-l="pt">O argumento, em detalhe</span>'
      '<span data-l="en">The argument, in detail</span></div>\n'
    + prose + "\n"
    + '<nav class="pn"><a href="concept_usage.html">&larr; <span data-l="pt">Guia de uso</span>'
      '<span data-l="en">Usage guide</span></a>'
      '<a href="concept_msd-model.html"><span data-l="pt">Modelo MSD</span>'
      '<span data-l="en">MSD model</span> &rarr;</a></nav>\n'
    + '<footer><p><b>Bolt Analysis Studio V2</b> — '
      '<span data-l="pt">dados do store canônico de validação</span>'
      '<span data-l="en">data from the canonical validation store</span>.</p>'
      '<p><code>python New_Theory/build_variable_explorer.py</code> '
      '<span data-l="pt">e então</span><span data-l="en">then</span> '
      '<code>python New_Theory/restyle_notafit.py</code></p></footer>\n'
    + "</main>\n</div>\n"
    + "\n".join(ov_scripts) + "\n"
    + "<script>" + OVL_JS + "</script>\n<script>" + SHELL_JS + "</script>\n"
    "</body>\n</html>\n")

P.write_text(page, encoding="utf-8")
print("OK: %d overlays, %d painéis de prosa, %d bytes" % (built, len(panels), len(page)))
