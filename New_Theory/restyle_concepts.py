# -*- coding: utf-8 -*-
"""Reestiliza as páginas de FUNDAMENTOS (concept_*.html) no VISUAL DO TUTORIAL DE
USO (dark, Bahnschrift, hero, sidebar de fundamentos + seções, animações),
PRESERVANDO os widgets interativos (decomp/runaway/energy/anatomy) e a prosa.

Reusa o CSS de conteúdo/widget do próprio explorador (_BASE_CSS + _CONCEPT_CSS, que
já é baseado em --variáveis) e só sobrepõe a "chrome" do tutorial + tokens dark.

    python New_Theory/build_variable_explorer.py     # gera as páginas base
    python New_Theory/restyle_concepts.py            # reestiliza todas

Não toca em not-a-fit (restyle_notafit.py) nem gallery (restyle_gallery.py),
que têm scripts próprios. Idempotente.
"""
import html as _html
import pathlib
import re
import sys

sys.path.insert(0, "src")
sys.path.insert(0, "New_Theory")
from build_variable_explorer import _BASE_CSS, _CONCEPT_CSS, CONCEPT_PAGES  # noqa: E402
import eq_to_mathml as _e2m  # noqa: E402

VE = pathlib.Path("New_Theory/variable_explorer")
SPECIAL = {"gallery", "not-a-fit"}
NAV = [(p["slug"], p["nav_pt"], p["nav_en"]) for p in CONCEPT_PAGES]

OVERRIDES = r"""
/* ===== chrome do tutorial (sobrepõe o explorador) ===== */
:root{
  --bg:#15161b; --panel:#1e1f27; --ink:#cdd6f4; --muted:#a6adc8; --line:#313244;
  --accent:#4aa3e0; --accent2:#f0868b; --ghost:#454a5a; --code-bg:#232530;
  --ok:#a6e3a1; --warn:#e5c07b; --side:#1a1b22; --side-w:274px;
  --bg2:#1a1b22; --line2:#3a3d4d;
  --disp:'Bahnschrift','DIN Alternate','Segoe UI',system-ui,sans-serif;
  --mono:'Consolas','Cascadia Code',monospace;
}
body{background:var(--bg);color:var(--ink);font-family:'Segoe UI',system-ui,sans-serif}
.wrap{display:grid;grid-template-columns:var(--side-w) minmax(0,1fr);max-width:1500px;margin:0 auto}
nav.toc{position:sticky;top:0;align-self:start;height:100vh;overflow-y:auto;padding:22px 15px 46px;border-right:1px solid var(--line);background:var(--side)}
nav.toc .brand{font-family:var(--disp);font-weight:700;letter-spacing:.4px;font-size:15px;color:#fff;line-height:1.2}
nav.toc .brand span{display:block;font-size:10.5px;font-weight:600;color:var(--accent);letter-spacing:1.4px;margin-top:3px}
nav.toc .lang{display:flex;gap:6px;margin:14px 4px 4px}
nav.toc .lang button{flex:1;background:var(--panel);border:1px solid var(--line);color:var(--muted);border-radius:7px;padding:5px;font-size:12px;cursor:pointer;font-family:var(--mono);transition:all .15s}
nav.toc .lang button.on{background:var(--accent);color:#08121c;border-color:var(--accent);font-weight:700}
nav.toc .sep{margin:16px 6px 6px;font-size:10.5px;letter-spacing:1.4px;text-transform:uppercase;color:var(--muted)}
nav.toc a{display:block;color:var(--muted);padding:5px 9px;border-radius:6px;font-size:13px;border-left:2px solid transparent;transition:transform .15s ease,background .15s,color .15s;text-decoration:none}
nav.toc a:hover{background:var(--panel);color:var(--ink);transform:translateX(2px)}
nav.toc a.active{background:var(--panel);color:#fff;border-left-color:var(--accent)}
nav.toc a.cur{color:#fff;font-weight:600}
main{margin:0;padding:0 clamp(18px,3.5vw,54px) 90px;min-width:0;max-width:1120px}
header.hero{margin:0 calc(-1*clamp(18px,3.5vw,54px)) 26px;padding:56px clamp(18px,3.5vw,54px) 34px;border-bottom:1px solid var(--line);position:relative;overflow:hidden;
  background:radial-gradient(1100px 320px at 18% -20%, #24344d66, transparent),radial-gradient(820px 300px at 92% -10%, #2c2140aa, transparent), var(--bg2)}
header.hero::before{content:"";position:absolute;inset:0;pointer-events:none;background-image:linear-gradient(var(--line) 1px,transparent 1px),linear-gradient(90deg,var(--line) 1px,transparent 1px);background-size:34px 34px;opacity:.09}
header.hero>*{position:relative}
header.hero .kicker{font-family:var(--mono);font-size:12px;letter-spacing:3px;text-transform:uppercase;color:var(--accent)}
header.hero h1{font-family:var(--disp);font-weight:700;letter-spacing:.4px;font-size:clamp(28px,4.4vw,46px);margin:8px 0 10px;color:#fff;line-height:1.03}
header.hero .lead{max-width:74ch;color:var(--muted);font-size:15.5px;margin:0}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:18px 20px;margin:18px 0}
h2.sec{font-family:var(--disp);font-weight:700;font-size:19px;color:#fff;scroll-margin-top:16px}
.eq{background:linear-gradient(180deg,#262832,var(--code-bg));border:1px solid var(--line);
  border-left:3px solid var(--accent);border-radius:10px;padding:12px 20px;margin:16px 0;
  color:#eaf0fc;box-shadow:0 3px 14px rgba(0,0,0,.28)}
.eq-line{display:flex;align-items:baseline;gap:6px 18px;flex-wrap:wrap;margin:9px 0;line-height:1.55}
.eq-line math{font-size:1.32rem;color:#eef3ff}
.eq-raw{font-family:var(--mono);white-space:pre;overflow-x:auto;font-size:1.02rem;color:#eaf0fc}
.eq .eq-cmt{color:var(--muted);font-family:'Segoe UI',system-ui,sans-serif;font-style:italic;font-size:.82em}
math{font-family:'Cambria Math','STIX Two Math','Latin Modern Math','Times New Roman',serif}
code{background:var(--code-bg);border:1px solid var(--line);color:#dfe6f5}
/* animações */
@keyframes ve-rise{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:none}}
.gprog{position:fixed;top:0;left:0;height:3px;width:0;z-index:100;background:linear-gradient(90deg,var(--accent),#cba6f7);box-shadow:0 0 10px var(--accent);transition:width .08s linear}
.reveal{opacity:0;transform:translateY(18px)}
.reveal.in{opacity:1;transform:none;transition:opacity .6s cubic-bezier(.2,.7,.2,1),transform .6s cubic-bezier(.2,.7,.2,1)}
header.hero .kicker{animation:ve-rise .7s cubic-bezier(.2,.7,.2,1) both}
header.hero h1{animation:ve-rise .7s .08s cubic-bezier(.2,.7,.2,1) both}
header.hero .lead{animation:ve-rise .7s .16s cubic-bezier(.2,.7,.2,1) both}
.cw canvas,.plotwrap canvas,#plot_an{cursor:crosshair}
@media(max-width:900px){.wrap{grid-template-columns:1fr}nav.toc{position:static;height:auto;border-right:0;border-bottom:1px solid var(--line)}}
@media(prefers-reduced-motion:reduce){.reveal,.reveal.in{opacity:1!important;transform:none!important;transition:none!important}header.hero .kicker,header.hero h1,header.hero .lead{animation:none}.gprog{display:none}nav.toc a:hover{transform:none}}
"""

SHELL_JS = r"""
(function(){
  var reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
  window.setLang=function(l){document.documentElement.dataset.lang=l;
    document.querySelectorAll('nav.toc .lang button').forEach(function(b){b.classList.toggle('on',b.getAttribute('data-l')===l);});
    if(window._cwRefresh)window._cwRefresh(); if(window.veRedraw)window.veRedraw();};
  setLang(document.documentElement.dataset.lang||'pt');
  if(!reduce){
    var bar=document.createElement('div');bar.className='gprog';document.body.appendChild(bar);
    function pg(){var hh=document.documentElement.scrollHeight-innerHeight;bar.style.width=(hh>0?scrollY/hh*100:0)+'%';}
    addEventListener('scroll',pg,{passive:true});addEventListener('resize',pg);pg();
    var vh=innerHeight||800;
    var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target);}});},{rootMargin:'0px 0px -6% 0px'});
    document.querySelectorAll('.panel,.widget').forEach(function(el){if(el.getBoundingClientRect().top>vh*0.9){el.classList.add('reveal');io.observe(el);}});
  }
  var links={};document.querySelectorAll('nav.toc a[href^="#"]').forEach(function(a){links[a.getAttribute('href').slice(1)]=a;});
  var aio=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){var a=links[e.target.id];
    if(a){for(var k in links)links[k].classList.remove('active');a.classList.add('active');}}});},{rootMargin:'-30% 0px -62% 0px'});
  Object.keys(links).forEach(function(id){var el=document.getElementById(id);if(el)aio.observe(el);});
})();
"""


def first_div(html, marker):
    start = html.index(marker)
    depth = 0
    for m in re.finditer(r"<div\b|</div>", html[start:]):
        depth += -1 if m.group() == "</div>" else 1
        if depth == 0:
            return html[start:start + m.end()], start + m.end()
    return html[start:], len(html)


def _improve_eq(content):
    """Renderiza as equações como MATEMÁTICA DE VERDADE (MathML) linha a linha:
    a matemática limpa vira MathML (subscritos/sobrescritos/símbolos), o
    pseudocódigo/prosa fica em monospace, e o comentário `(…)` no fim é atenuado."""
    def fix(m):
        rows = []
        for ln in m.group(1).split("\n"):
            if not ln.strip():
                continue
            mm = re.match(r"^(.*?)(\s{2,})(\((?:[^()]|\([^()]*\))*\))\s*$", ln)
            if mm:
                mathpart, gap, cmt = mm.group(1), mm.group(2), mm.group(3)
                cmt_html = '<span class="eq-cmt">%s</span>' % cmt
            else:
                mathpart, gap, cmt_html = ln, "", ""
            raw = _html.unescape(mathpart)
            if _e2m.is_convertible(raw):
                rows.append('<div class="eq-line">%s%s</div>'
                            % (_e2m.to_mathml(raw), cmt_html))
            else:
                rows.append('<div class="eq-line eq-raw">%s%s%s</div>'
                            % (mathpart, gap, cmt_html))
        return '<div class="eq">' + "".join(rows) + "</div>"
    return re.sub(r'<div class="eq">(.*?)</div>', fix, content, flags=re.S)


def restyle_one(slug):
    path = VE / ("concept_%s.html" % slug)
    src = path.read_text(encoding="utf-8")
    main = re.search(r'<main class="main">(.*)</main>', src, re.S).group(1)

    hm = re.search(r'<h1 class="name">(.*?)</h1>', main, re.S)
    title = hm.group(1).strip()
    after = main[hm.end():]

    sub_inner = ""
    if re.match(r'\s*<div class="sub">', after):
        sub_block, sub_end = first_div(after, '<div class="sub">')
        mi = re.match(r'<div class="sub">(.*)</div>\s*$', sub_block, re.S)
        sub_inner = mi.group(1).strip() if mi else ""
        content = after[sub_end:]
    else:
        content = after

    content = _improve_eq(content)          # apresentação das equações

    # âncoras + títulos das seções para o sumário lateral
    secs = []

    def _sec(m):
        i = len(secs)
        secs.append(("s%d" % i, m.group(1)))
        return '<h2 class="sec" id="s%d">%s</h2>' % (i, m.group(1))
    content = re.sub(r'<h2 class="sec">(.*?)</h2>', _sec, content, flags=re.S)

    # scripts: mantém dados + JS do widget; descarta o shell do explorador
    scripts = re.findall(r"<script>.*?</script>", src, re.S)
    keep = "\n".join(s for s in scripts if "veToggleTheme" not in s and s.strip())

    nav_items = "".join(
        '<a href="concept_%s.html"%s><span data-l="pt">%s</span>'
        '<span data-l="en">%s</span></a>'
        % (sl, ' class="cur"' if sl == slug else "", pt, en)
        for sl, pt, en in NAV)
    sec_items = "".join('<a href="#%s">%s</a>' % (sid, t) for sid, t in secs)

    sidebar = (
        '<nav class="toc">'
        '<div class="brand">Bolt Analysis Studio<span>V2 · FUNDAMENTOS</span></div>'
        '<div class="lang"><button data-l="pt" onclick="setLang(\'pt\')">PT</button>'
        '<button data-l="en" onclick="setLang(\'en\')">EN</button></div>'
        '<div class="sep"><span data-l="pt">Navegação</span><span data-l="en">Navigation</span></div>'
        '<a href="index.html">← <span data-l="pt">Explorador</span><span data-l="en">Explorer</span></a>'
        + (('<div class="sep"><span data-l="pt">Nesta página</span>'
            '<span data-l="en">On this page</span></div>' + sec_items) if sec_items else "")
        + '<div class="sep"><span data-l="pt">Fundamentos</span><span data-l="en">Foundations</span></div>'
        + nav_items + '</nav>')

    hero = ('<header class="hero">'
            '<div class="kicker"><span data-l="pt">Fundamentos</span>'
            '<span data-l="en">Foundations</span></div>'
            '<h1>%s</h1>' % title
            + ('<div class="lead">%s</div>' % sub_inner if sub_inner else "")
            + '</header>')

    page = (
        "<!DOCTYPE html>\n"
        '<html lang="pt" data-lang="pt">\n<head>\n'
        '<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>%s — BAS V2</title>\n" % re.sub(r"<[^>]+>", "", title)[:60]
        + "<style>" + _BASE_CSS + _CONCEPT_CSS + OVERRIDES + "</style>\n</head>\n<body>\n"
        + '<div class="wrap">\n' + sidebar + "\n<main>\n" + hero + "\n" + content
        + "\n</main>\n</div>\n" + keep
        + "\n<script>" + SHELL_JS + "</script>\n</body>\n</html>\n")
    path.write_text(page, encoding="utf-8")
    return len(secs), bool(keep.strip())


done = []
for p in CONCEPT_PAGES:
    if p["slug"] in SPECIAL:
        continue
    try:
        nsec, has_widget = restyle_one(p["slug"])
        done.append((p["slug"], nsec, has_widget))
    except Exception as e:  # noqa
        print("FALHOU %s: %r" % (p["slug"], e))
for sl, nsec, hw in done:
    print("OK %-14s | %d seções | widget=%s" % (sl, nsec, hw))
print("Total: %d páginas reestilizadas" % len(done))
