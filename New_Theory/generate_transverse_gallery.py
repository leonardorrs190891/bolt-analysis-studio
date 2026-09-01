"""Galeria HTML dado x modelo COM ERROS — biblioteca TRANSVERSAL (46 curvas).

Le transverse_provenance.json (naive-frozen vs adotado per-rig) e gera
validation_html/transverse_provenance.html: grade de SVGs por fonte, cada um com
pontos do dado, modelo naive-frozen (tracejado) + adotado (solido) e barras de
erro |adotado-dado|; tabela-resumo. Paralelo transversal do estudo axial (sec4.40).

Run: python New_Theory/generate_transverse_gallery.py
"""
from __future__ import annotations
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "New_Theory/transverse_provenance.json"
OUT = ROOT / "New_Theory/validation_html/transverse_provenance.html"

W, H = 400, 270
ML, MR, MT, MB = 52, 14, 16, 40


def _lx(n, nmax):
    hi = math.log10(max(nmax, 10))
    lo = hi - max(math.log10(max(nmax, 10)), 2.4)      # >=2.4 decadas
    v = math.log10(max(n, 1))
    x = ML + (v - lo) / (hi - lo) * (W - ML - MR)
    return min(max(x, ML), W - MR)


def _ly(y):
    yy = MT + (1 - (y - 0.0) / 1.08) * (H - MT - MB)
    return min(max(yy, MT - 8), H - MB)      # clampa overshoot do naive (>1.08)


def _poly(xs, ys, nmax, **attr):
    pts = " ".join(f"{_lx(x,nmax):.1f},{_ly(y):.1f}" for x, y in zip(xs, ys))
    a = " ".join(f'{k.replace("_","-")}="{v}"' for k, v in attr.items())
    return f'<polyline points="{pts}" fill="none" {a}/>'


def svg(e):
    import numpy as np
    nmax = e["n_max"]
    dx, dy = e["data"]["x"], e["data"]["y"]
    nv, ad = e["naive"], e["adopted"]
    s = [f'<svg viewBox="0 0 {W} {H}" class="plot" xmlns="http://www.w3.org/2000/svg">']
    for yv in (0.0, 0.25, 0.5, 0.75, 1.0):
        yy = _ly(yv)
        s.append(f'<line x1="{ML}" y1="{yy:.1f}" x2="{W-MR}" y2="{yy:.1f}" class="grid"/>')
        s.append(f'<text x="{ML-6}" y="{yy+3:.1f}" class="tick" text-anchor="end">{yv:.2f}</text>')
    d = int(math.log10(max(nmax, 10)))
    for ex in range(max(d - 3, 0), d + 1):
        xx = _lx(10 ** ex, nmax)
        s.append(f'<line x1="{xx:.1f}" y1="{MT}" x2="{xx:.1f}" y2="{H-MB}" class="grid"/>')
        s.append(f'<text x="{xx:.1f}" y="{H-MB+14}" class="tick" text-anchor="middle">1e{ex}</text>')
    mi = np.interp(dx, ad["x"], ad["y"])
    for x, yd, ym in zip(dx, dy, mi):
        s.append(f'<line x1="{_lx(x,nmax):.1f}" y1="{_ly(yd):.1f}" '
                 f'x2="{_lx(x,nmax):.1f}" y2="{_ly(ym):.1f}" class="err"/>')
    s.append(_poly(nv["x"], nv["y"], nmax, stroke="var(--hb)", stroke_width="1.4",
                   stroke_dasharray="4 3", opacity="0.8"))
    s.append(_poly(ad["x"], ad["y"], nmax, stroke="var(--di)", stroke_width="2.2"))
    for x, y in zip(dx, dy):
        s.append(f'<circle cx="{_lx(x,nmax):.1f}" cy="{_ly(y):.1f}" r="2.5" class="pt"/>')
    s.append(f'<text x="{(ML+W-MR)/2:.0f}" y="{H-4}" class="axl" text-anchor="middle">ciclos N (log)</text>')
    s.append(f'<text x="12" y="{(MT+H-MB)/2:.0f}" class="axl" text-anchor="middle" '
             f'transform="rotate(-90 12 {(MT+H-MB)/2:.0f})">F / F&#8320; [&#8211;]</text>')
    s.append('</svg>')
    return "".join(s)


def card(e):
    nv, ad = e["naive"]["mae"], e["adopted"]["mae"]
    good = ad < nv - 1e-3
    badge = (f'<span class="delta good">&#9660; {(nv-ad):.2f}</span>' if good
             else '<span class="delta flat">&#8776;</span>')
    return f'''<div class="card">
  <div class="ct"><b>{e["csv"].replace(".csv","")}</b> {badge}</div>
  {svg(e)}
  <div class="cf">MAE naive-frozen <b>{nv:.3f}</b> &#8594; adotado per-rig <b>{ad:.3f}</b>
     &#183; amp {e["amp_mm"]:.2f} mm</div>
</div>'''


def main():
    import numpy as np
    res = json.loads(DATA.read_text(encoding="utf-8"))
    mn = float(np.mean([e["naive"]["mae"] for e in res]))
    ma = float(np.mean([e["adopted"]["mae"] for e in res]))
    groups = {}
    for e in res:
        groups.setdefault(e["source"], []).append(e)
    body = []
    # tabela por fonte
    rows = ""
    for src, items in sorted(groups.items()):
        gn = np.mean([e["naive"]["mae"] for e in items])
        ga = np.mean([e["adopted"]["mae"] for e in items])
        rows += (f'<tr><td>{src}</td><td>{len(items)}</td><td>{gn:.3f}</td>'
                 f'<td class="good">{ga:.3f}</td></tr>')
    body.append(f'''<table class="sum"><thead><tr><th>Fonte</th><th>curvas</th>
      <th>MAE naive-frozen</th><th>MAE adotado</th></tr></thead><tbody>{rows}
      <tr class="tot"><td>M&#201;DIA ({len(res)})</td><td>&#8211;</td>
      <td>{mn:.3f}</td><td class="good">{ma:.3f}</td></tr></tbody></table>''')
    for src, items in sorted(groups.items()):
        body.append(f'<h2>{src} &#183; {len(items)} curvas</h2><div class="grid">'
                    + "".join(card(e) for e in items) + '</div>')
    html = f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Proveni&#234;ncia do n&#237;vel transversal &#8212; dado&#215;modelo com erros</title>
<style>
:root{{--bg:#faf9f7;--fg:#1c1a17;--mut:#6b655c;--card:#fff;--bd:#e6e1d8;
  --hb:#b08968;--di:#2f6f8f;--err:#c0392b;--pt:#1c1a17;--good:#1a7a4c;--accent:#2f6f8f}}
@media (prefers-color-scheme:dark){{:root{{--bg:#16140f;--fg:#ece7de;--mut:#9a938a;
  --card:#211e18;--bd:#332e26;--hb:#c9a27a;--di:#6bb6d6;--err:#e8776b;--pt:#ece7de;--good:#5fd39a}}}}
:root[data-theme=dark]{{--bg:#16140f;--fg:#ece7de;--mut:#9a938a;--card:#211e18;--bd:#332e26;
  --hb:#c9a27a;--di:#6bb6d6;--err:#e8776b;--pt:#ece7de;--good:#5fd39a}}
:root[data-theme=light]{{--bg:#faf9f7;--fg:#1c1a17;--mut:#6b655c;--card:#fff;--bd:#e6e1d8;
  --hb:#b08968;--di:#2f6f8f;--err:#c0392b;--pt:#1c1a17;--good:#1a7a4c}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--fg);
  font:15px/1.55 -apple-system,Segoe UI,Roboto,sans-serif;padding:28px 20px 60px}}
.wrap{{max-width:1180px;margin:0 auto}}
h1{{font-size:1.5rem;margin:0 0 4px;letter-spacing:-.01em}}
.lede{{color:var(--mut);margin:0 0 8px;max-width:74ch}}
.note{{background:var(--card);border:1px solid var(--bd);border-left:3px solid var(--accent);
  border-radius:8px;padding:10px 14px;margin:12px 0 20px;font-size:.86rem;color:var(--fg);max-width:80ch}}
h2{{font-size:1rem;text-transform:uppercase;letter-spacing:.06em;color:var(--accent);
  margin:28px 0 10px;border-bottom:1px solid var(--bd);padding-bottom:5px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:14px}}
.card{{background:var(--card);border:1px solid var(--bd);border-radius:10px;padding:10px 12px}}
.plot{{width:100%;height:auto;display:block}}
line.grid{{stroke:var(--bd);stroke-width:.6}}
.tick{{fill:var(--mut);font-size:9px}}.axl{{fill:var(--mut);font-size:10px}}
.err{{stroke:var(--err);stroke-width:2.4;opacity:.5}}.pt{{fill:var(--pt)}}
.ct{{font-size:.86rem;margin-bottom:2px;display:flex;justify-content:space-between;align-items:center;gap:6px}}
.cf{{font-size:.74rem;color:var(--mut);margin-top:6px}}
.delta{{font-size:.72rem;font-weight:600;white-space:nowrap}}.delta.good{{color:var(--good)}}.delta.flat{{color:var(--mut)}}
.sum{{border-collapse:collapse;width:100%;margin:6px 0 8px;font-size:.84rem}}
.sum th,.sum td{{text-align:right;padding:5px 12px;border-bottom:1px solid var(--bd)}}
.sum th:first-child,.sum td:first-child{{text-align:left}}
.sum .tot{{font-weight:700}}.sum .good{{color:var(--good);font-weight:600}}
.legend{{display:flex;gap:18px;flex-wrap:wrap;font-size:.8rem;color:var(--mut);margin:10px 0 4px}}
.legend b{{color:var(--fg)}}.sw{{display:inline-block;width:22px;height:0;vertical-align:middle;margin-right:5px}}
.back{{font-size:.8rem;margin:0 0 10px}}.back a{{color:var(--accent);text-decoration:none}}
</style></head><body><div class="wrap">
<p class="back"><a href="index.html">&#8592; &#237;ndice de valida&#231;&#227;o</a></p>
<h1>Proveni&#234;ncia do n&#237;vel <b>transversal</b> &#8212; dado &#215; modelo, com erros</h1>
<p class="lede">Paralelo transversal do estudo axial (&#167;4.40). 46 curvas, 7 fontes.
Contraste: <b>naive-frozen</b> (config congelada, c_bend=1, sem per-rig) vs <b>adotado</b>
(per-rig: c_bend + floor do fim do dado).</p>
<div class="note"><b>Contraste com o axial (&#167;4.40 fronteira):</b> no axial o n&#237;vel &#233;
<b>data-impl&#237;cito</b> (emb da queda-inicial, uma LEI f&#237;sica emb&#8733;A_F/F&#8320; R&#178;=0.89)
&#8212; melhora 90%. No transversal a queda-inicial &#233; <b>loosening/creep</b> (n&#227;o embedding),
ent&#227;o o n&#237;vel &#233; <b>c_bend per-rig fitado</b> (n&#227;o uma lei limpa &#8212; &#167;4.35) +
floor do fim do dado (proveni&#234;ncia parcial). Melhora 78% (0.330&#8594;0.072), mas via <i>fit
per-rig</i>, n&#227;o proveni&#234;ncia pura. &#201; o padr&#227;o do &#167;8: formas transferem,
n&#237;veis/constantes s&#227;o per-rig &#8212; e s&#243; o axial tem o n&#237;vel <i>leg&#237;vel</i> do dado.</div>
<div class="legend">
  <span><span class="sw" style="border-top:2.2px solid var(--di)"></span><b>modelo</b> adotado per-rig</span>
  <span><span class="sw" style="border-top:2px dashed var(--hb)"></span>modelo naive-frozen (c_bend=1)</span>
  <span><span class="sw" style="border-top:2.4px solid var(--err);opacity:.5"></span>erro |adotado&#8722;dado|</span>
  <span>&#9679; dado</span>
</div>
{''.join(body)}
</div></body></html>'''
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(f"escrito: {OUT}  ({len(res)} curvas; MAE naive {mn:.3f} -> adotado {ma:.3f})")


if __name__ == "__main__":
    main()
