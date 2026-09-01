# -*- coding: utf-8 -*-
"""Reestiliza New_Theory/variable_explorer/concept_gallery.html no VISUAL DO
TUTORIAL DE USO (dark, Bahnschrift, hero, sidebar de fontes, animações),
preservando os plots interativos + os dados (GDATA) + a lógica (_GALLERY_JS).

Rode DEPOIS de build_variable_explorer.py (que regenera a galeria no estilo do
explorador):

    python New_Theory/restyle_gallery.py

Idempotente: extrai o widget da galeria por contagem de <div>, então funciona
tanto no arquivo recém-gerado quanto no já reestilizado.
"""
import pathlib
import re

P = pathlib.Path("New_Theory/variable_explorer/concept_gallery.html")
src = P.read_text(encoding="utf-8")


def first_div(html, marker):
    """Extrai o <div ...>...</div> completo que começa em `marker` (conta profundidade)."""
    start = html.index(marker)
    depth = 0
    for m in re.finditer(r"<div\b|</div>", html[start:]):
        depth += -1 if m.group() == "</div>" else 1
        if depth == 0:
            return html[start:start + m.end()]
    return html[start:]


# --- widget interativo da galeria (summary + controls + seções por fonte) ---
widget = first_div(src, '<div id="cw"')

# âncoras nas seções por fonte + lista (data_src, nome) para o sidebar
srcs = re.findall(
    r'<section class="gal-src"[^>]*data-src="([^"]+)"[^>]*>\s*'
    r'<h3 class="gal-srch"><a[^>]*>([^<]*?)\s*(?:&rarr;|→)', widget)
widget = re.sub(r'<section class="gal-src"(?![^>]*\bid=)\s+data-src="([^"]+)"',
                r'<section class="gal-src" id="src-\1" data-src="\1"', widget)

# --- scripts: mantém GDATA + _GALLERY_JS; descarta o shell do explorador ---
scripts = re.findall(r"<script>.*?</script>", src, re.S)
gdata = next(s for s in scripts if "const GDATA" in s)
galjs = next(s for s in scripts if "drawCard" in s and "const GDATA" not in s)

side_items = "".join(
    '<a href="#src-%s" data-src="%s">%s</a>' % (ds, ds, nm) for ds, nm in srcs)

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
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--body);
  font-size:15px;line-height:1.6;-webkit-font-smoothing:antialiased}
a{color:var(--accent);text-decoration:none} a:hover{text-decoration:underline}
code{font-family:var(--mono);background:var(--code-bg);border:1px solid var(--line);
  border-radius:4px;padding:.05em .35em;font-size:.88em;color:#dfe6f5}
[data-lang="pt"] [data-l="en"]{display:none}
[data-lang="en"] [data-l="pt"]{display:none}

/* ---- layout ---- */
.wrap{display:grid;grid-template-columns:var(--side-w) minmax(0,1fr);max-width:1520px;margin:0 auto}
nav.toc{position:sticky;top:0;align-self:start;height:100vh;overflow-y:auto;
  padding:22px 15px 44px;border-right:1px solid var(--line);background:var(--side)}
nav.toc .brand{font-family:var(--disp);font-weight:700;letter-spacing:.4px;font-size:15px;color:#fff;line-height:1.2}
nav.toc .brand span{display:block;font-size:10.5px;font-weight:600;color:var(--accent);letter-spacing:1.4px;margin-top:3px}
nav.toc .lang{display:flex;gap:6px;margin:14px 4px 4px}
nav.toc .lang button{flex:1;background:var(--panel);border:1px solid var(--line);color:var(--muted);
  border-radius:7px;padding:5px;font-size:12px;cursor:pointer;font-family:var(--mono);transition:all .15s}
nav.toc .lang button:hover{border-color:var(--accent);color:var(--ink)}
nav.toc .lang button.on{background:var(--accent);color:#08121c;border-color:var(--accent);font-weight:700}
nav.toc .sep{margin:16px 6px 6px;font-size:10.5px;letter-spacing:1.4px;text-transform:uppercase;color:var(--muted)}
nav.toc a{display:block;color:var(--muted);padding:5px 9px;border-radius:6px;font-size:13px;
  border-left:2px solid transparent;transition:transform .15s ease,background .15s,color .15s}
nav.toc a:hover{background:var(--panel);color:var(--ink);text-decoration:none;transform:translateX(2px)}
nav.toc a.active{background:var(--panel);color:#fff;border-left-color:var(--accent)}
main{padding:0 clamp(18px,3.5vw,54px) 90px;min-width:0}

/* ---- hero ---- */
header.hero{margin:0 calc(-1*clamp(18px,3.5vw,54px)) 26px;padding:58px clamp(18px,3.5vw,54px) 34px;
  border-bottom:1px solid var(--line);position:relative;overflow:hidden;
  background:radial-gradient(1100px 320px at 18% -20%, #24344d66, transparent),
             radial-gradient(820px 300px at 92% -10%, #2c2140aa, transparent), var(--bg2)}
header.hero::before{content:"";position:absolute;inset:0;pointer-events:none;
  background-image:linear-gradient(var(--line) 1px,transparent 1px),
                   linear-gradient(90deg,var(--line) 1px,transparent 1px);
  background-size:34px 34px;opacity:.09}
header.hero>*{position:relative}
header.hero .kicker{font-family:var(--mono);font-size:12px;letter-spacing:3px;text-transform:uppercase;color:var(--accent)}
header.hero h1{font-family:var(--disp);font-weight:700;letter-spacing:.4px;
  font-size:clamp(29px,4.6vw,48px);margin:8px 0 10px;color:#fff;line-height:1.02}
header.hero p.lead{max-width:70ch;color:var(--muted);font-size:15.5px;margin:0}

/* ---- galeria (classes preservadas, tokens dark) ---- */
.widget{margin-top:6px}
.gal-summary{display:flex;flex-wrap:wrap;gap:16px 30px;padding:18px 20px;
  background:linear-gradient(180deg,var(--panel2),var(--panel));
  border:1px solid var(--line);border-radius:14px;margin:6px 0 20px}
.gal-stat{font-size:.9rem;color:var(--muted);display:flex;flex-direction:column;gap:2px}
.gal-stat b{color:#fff;font-size:1.7rem;font-family:var(--disp);line-height:1}
.gal-controls{display:flex;flex-wrap:wrap;gap:9px;align-items:center;margin:14px 0 6px}
.gal-flt{cursor:pointer;font-size:.82rem;padding:5px 14px;border:1px solid var(--line);
  border-radius:16px;color:var(--muted);transition:all .16s ease}
.gal-flt:hover{border-color:var(--accent);color:var(--ink)}
.gal-flt[data-on]{background:var(--accent);color:#08121c;border-color:var(--accent);font-weight:700}
.gal-only{font-size:.82rem;color:var(--muted);margin-left:auto;display:flex;align-items:center;gap:5px}
.gal-only input{accent-color:var(--accent)}
.gal-src{margin:28px 0}
.gal-srch{font-family:var(--disp);font-weight:700;font-size:1.2rem;margin:0 0 3px;
  border-bottom:1px solid var(--line);padding-bottom:7px;color:#fff}
.gal-srch a{color:var(--accent)}
.gal-srcn{font-size:.8rem;color:var(--muted);font-weight:400;font-family:var(--mono)}
.gal-blurb{font-size:.85rem;color:var(--muted);margin:5px 0 11px}
.gal-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(252px,1fr));gap:14px}
.gal-card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:10px 12px;
  transition:transform .18s ease,box-shadow .18s ease,border-color .18s ease}
.gal-card:hover{transform:translateY(-3px);box-shadow:0 12px 26px rgba(0,0,0,.4);border-color:var(--line2)}
.gal-cap{display:flex;justify-content:space-between;align-items:baseline;gap:6px;font-size:.82rem}
.gal-nm{font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:var(--ink)}
.gal-badge{flex:0 0 auto;font-family:var(--mono);font-size:.72rem;padding:1px 7px;border-radius:8px;border:1px solid currentColor}
.gal-badge.ok{color:var(--ok)} .gal-badge.mid{color:var(--accent2)} .gal-badge.hi{color:var(--warn)}
.gal-cv{width:100%;height:auto;display:block;margin:6px 0}
.gal-cond{font-size:.72rem;color:var(--muted);font-family:var(--mono)}
.gal-cav{font-size:.72rem;color:var(--warn);margin-top:4px;line-height:1.35}
.gal-report{display:inline-block;margin-top:7px;font-size:.74rem;color:var(--accent)}
.gal-csv{display:inline-block;margin:5px 8px 0 0;font-size:.74rem;color:var(--accent)}

footer{color:var(--muted);font-size:12.5px;padding:34px 0 0;border-top:1px solid var(--line);margin-top:30px;line-height:1.7}
footer code{font-size:11.5px}

/* ---- animações ---- */
@keyframes ve-rise{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:none}}
.gprog{position:fixed;top:0;left:0;height:3px;width:0;z-index:100;
  background:linear-gradient(90deg,var(--accent),#cba6f7);box-shadow:0 0 10px var(--accent);transition:width .08s linear}
.gal-summary.in,.gal-controls.in,.gal-src.in{animation:ve-rise .6s cubic-bezier(.2,.7,.2,1) both}
header.hero .kicker{animation:ve-rise .7s cubic-bezier(.2,.7,.2,1) both}
header.hero h1{animation:ve-rise .7s .08s cubic-bezier(.2,.7,.2,1) both}
header.hero p.lead{animation:ve-rise .7s .16s cubic-bezier(.2,.7,.2,1) both}

@media(max-width:900px){
  .wrap{grid-template-columns:1fr}
  nav.toc{position:static;height:auto;border-right:0;border-bottom:1px solid var(--line)}
}
@media(prefers-reduced-motion:reduce){
  .gal-summary.in,.gal-controls.in,.gal-src.in,
  header.hero .kicker,header.hero h1,header.hero p.lead{animation:none}
  .gprog{display:none}
  .gal-card:hover{transform:none}
  nav.toc a:hover{transform:none}
}
"""

MYJS = r"""
(function(){
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  window.setLang=function(l){document.documentElement.dataset.lang=l;
    document.querySelectorAll('nav.toc .lang button').forEach(function(b){
      b.classList.toggle('on', b.getAttribute('data-l')===l);});
    if(window._cwRefresh)window._cwRefresh();};
  setLang(document.documentElement.dataset.lang||'pt');

  if(!reduce){
    var bar=document.createElement('div');bar.className='gprog';document.body.appendChild(bar);
    function pg(){var h=document.documentElement.scrollHeight-innerHeight;
      bar.style.width=(h>0?scrollY/h*100:0)+'%';}
    addEventListener('scroll',pg,{passive:true});addEventListener('resize',pg);pg();
    var vh=innerHeight||800;
    var io=new IntersectionObserver(function(es){es.forEach(function(e){
      if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target);}});},
      {rootMargin:'0px 0px -6% 0px'});
    document.querySelectorAll('.gal-summary,.gal-controls,.gal-src').forEach(function(el){
      if(el.getBoundingClientRect().top>vh*0.9)io.observe(el);});
  }

  var links={};document.querySelectorAll('nav.toc a[data-src]').forEach(function(a){links[a.getAttribute('data-src')]=a;});
  var aio=new IntersectionObserver(function(es){es.forEach(function(e){
    if(e.isIntersecting){var a=links[e.target.getAttribute('data-src')];
      if(a){for(var k in links)links[k].classList.remove('active');a.classList.add('active');}}});},
    {rootMargin:'-38% 0px -56% 0px'});
  document.querySelectorAll('.gal-src').forEach(function(s){aio.observe(s);});
})();
"""

hero = (
    '<header class="hero">'
    '<div class="kicker"><span data-l="pt">Validação · modelo vs dado</span>'
    '<span data-l="en">Validation · model vs data</span></div>'
    '<h1><span data-l="pt">Galeria de validação</span><span data-l="en">Validation gallery</span></h1>'
    '<p class="lead"><span data-l="pt">Cada card confronta a <b>previsão</b> do modelo (linha) '
    'com o <b>dado</b> do artigo (pontos): MAE por caso, agrupado por fonte, com link para o '
    'report completo e download do CSV. Os gráficos desenham ao rolar.</span>'
    '<span data-l="en">Each card confronts the model <b>prediction</b> (line) with the paper '
    '<b>data</b> (points): per-case MAE, grouped by source, with a link to the full report and '
    'CSV download. Plots draw as you scroll.</span></p>'
    '</header>')

sidebar = (
    '<nav class="toc">'
    '<div class="brand">Bolt Analysis Studio<span>V2 · GALERIA DE VALIDAÇÃO</span></div>'
    '<div class="lang"><button data-l="pt" onclick="setLang(\'pt\')">PT</button>'
    '<button data-l="en" onclick="setLang(\'en\')">EN</button></div>'
    '<div class="sep"><span data-l="pt">Navegação</span><span data-l="en">Navigation</span></div>'
    '<a href="index.html">← <span data-l="pt">Explorador</span><span data-l="en">Explorer</span></a>'
    '<a href="concept_usage.html"><span data-l="pt">Guia de uso</span><span data-l="en">Usage guide</span></a>'
    '<div class="sep"><span data-l="pt">Fontes</span><span data-l="en">Sources</span></div>'
    + side_items +
    '</nav>')

footer = (
    '<footer><p><b>Bolt Analysis Studio V2</b> — '
    '<span data-l="pt">galeria de validação do store canônico</span>'
    '<span data-l="en">validation gallery from the canonical store</span>.</p>'
    '<p><span data-l="pt">Reprodutibilidade: </span>'
    '<code>python New_Theory/build_variable_explorer.py</code> '
    '<span data-l="pt">e então</span><span data-l="en">then</span> '
    '<code>python New_Theory/restyle_gallery.py</code>.</p></footer>')

page = (
    "<!DOCTYPE html>\n"
    '<html lang="pt" data-lang="pt">\n<head>\n'
    '<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    "<title>Galeria de validação — Bolt Analysis Studio V2</title>\n"
    "<style>" + CSS + "</style>\n</head>\n<body>\n"
    '<div class="wrap">\n' + sidebar + "\n<main>\n" + hero + "\n"
    + widget + "\n" + footer + "\n</main>\n</div>\n"
    + gdata + "\n" + galjs + "\n<script>" + MYJS + "</script>\n"
    "</body>\n</html>\n")

P.write_text(page, encoding="utf-8")
print("OK: %d fontes no sidebar, %d bytes escritos" % (len(srcs), len(page)))
