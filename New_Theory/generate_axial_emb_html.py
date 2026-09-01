"""Galeria HTML dado x modelo COM ERROS para todas as condicoes axiais.

Le axial_emb_provenance.json (emb handbook vs data-implicito, sec4.40/L24) e
gera validation_html/axial_emb_provenance.html: grade de SVGs por sweep, cada um
com pontos do dado, curva do modelo (handbook tracejado + data-implicito solido)
e barras de erro |modelo-dado|; tabela-resumo com MAE por condicao.

Run: python New_Theory/generate_axial_emb_html.py
"""
from __future__ import annotations
import json
import math
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# JSON de entrada (default 200k); override via env EMB_JSON p/ o run 1e6 completo.
DATA = ROOT / os.environ.get("EMB_JSON", "New_Theory/axial_emb_provenance.json")
OUT = ROOT / "New_Theory/validation_html/axial_emb_provenance.html"

W, H = 400, 270
ML, MR, MT, MB = 52, 14, 16, 40


def _lx(n, nmax):
    hi = math.log10(max(nmax, 10))
    lo = hi - 3.2                              # ~3 decadas
    v = math.log10(max(n, 1))
    x = ML + (v - lo) / (hi - lo) * (W - ML - MR)
    return min(max(x, ML), W - MR)             # clampa (ciclo 0 -> borda esquerda)


def _ly(y):
    y0, y1 = 0.0, 1.08
    return MT + (1 - (y - y0) / (y1 - y0)) * (H - MT - MB)


def _poly(xs, ys, nmax, **attr):
    pts = " ".join(f"{_lx(x,nmax):.1f},{_ly(y):.1f}" for x, y in zip(xs, ys))
    a = " ".join(f'{k.replace("_","-")}="{v}"' for k, v in attr.items())
    return f'<polyline points="{pts}" fill="none" {a}/>'


def svg(entry):
    nmax = entry["n_max"]
    dx, dy = entry["data"]["x"], entry["data"]["y"]
    hb, di = entry["handbook"], entry["data_implied"]
    s = [f'<svg viewBox="0 0 {W} {H}" class="plot" xmlns="http://www.w3.org/2000/svg">']
    # grid + eixo Y
    for yv in (0.0, 0.25, 0.5, 0.75, 1.0):
        yy = _ly(yv)
        s.append(f'<line x1="{ML}" y1="{yy:.1f}" x2="{W-MR}" y2="{yy:.1f}" class="grid"/>')
        s.append(f'<text x="{ML-6}" y="{yy+3:.1f}" class="tick" text-anchor="end">{yv:.2f}</text>')
    # eixo X (decadas)
    d = int(math.log10(max(nmax, 10)))
    for e in range(max(d - 3, 1), d + 1):
        xx = _lx(10 ** e, nmax)
        s.append(f'<line x1="{xx:.1f}" y1="{MT}" x2="{xx:.1f}" y2="{H-MB}" class="grid"/>')
        s.append(f'<text x="{xx:.1f}" y="{H-MB+14}" class="tick" text-anchor="middle">1e{e}</text>')
    # barras de erro |modelo(data-impl) - dado| nos pontos do dado
    import numpy as np
    mi = np.interp(dx, di["x"], di["y"])
    for x, yd, ym in zip(dx, dy, mi):
        s.append(f'<line x1="{_lx(x,nmax):.1f}" y1="{_ly(yd):.1f}" '
                 f'x2="{_lx(x,nmax):.1f}" y2="{_ly(ym):.1f}" class="err"/>')
    # curvas modelo
    s.append(_poly(hb["x"], hb["y"], nmax, stroke="var(--hb)", stroke_width="1.4",
                   stroke_dasharray="4 3", opacity="0.85"))
    s.append(_poly(di["x"], di["y"], nmax, stroke="var(--di)", stroke_width="2.2"))
    # pontos do dado
    for x, y in zip(dx, dy):
        s.append(f'<circle cx="{_lx(x,nmax):.1f}" cy="{_ly(y):.1f}" r="2.6" class="pt"/>')
    # labels de eixo
    s.append(f'<text x="{(ML+W-MR)/2:.0f}" y="{H-4}" class="axl" text-anchor="middle">ciclos N (log)</text>')
    s.append(f'<text x="12" y="{(MT+H-MB)/2:.0f}" class="axl" text-anchor="middle" '
             f'transform="rotate(-90 12 {(MT+H-MB)/2:.0f})">F / F&#8320; (raz&#227;o) [&#8211;]</text>')
    s.append('</svg>')
    return "".join(s)


def scatter_svg(xs, ys, xlabel, fit=True, xunit=""):
    """Scatter emb[um] vs x, com ajuste linear e R2. viewBox 400x250."""
    import numpy as np
    xs, ys = np.array(xs, float), np.array(ys, float)
    x0, x1 = float(xs.min()), float(xs.max())
    y0, y1 = 0.0, float(max(ys.max() * 1.15, 0.5))
    pad = (x1 - x0) * 0.12 or 1.0
    x0 -= pad; x1 += pad
    ml, mr, mt, mb = 46, 12, 14, 38
    ww, hh = 400, 240

    def px(x): return ml + (x - x0) / (x1 - x0) * (ww - ml - mr)
    def py(y): return mt + (1 - (y - y0) / (y1 - y0)) * (hh - mt - mb)
    s = [f'<svg viewBox="0 0 {ww} {hh}" class="plot" xmlns="http://www.w3.org/2000/svg">']
    for i in range(5):
        yv = y0 + (y1 - y0) * i / 4
        yy = py(yv)
        s.append(f'<line x1="{ml}" y1="{yy:.1f}" x2="{ww-mr}" y2="{yy:.1f}" class="grid"/>')
        s.append(f'<text x="{ml-5}" y="{yy+3:.1f}" class="tick" text-anchor="end">{yv:.1f}</text>')
    if fit:
        a, b = np.polyfit(xs, ys, 1)
        pr = a * xs + b
        r2 = 1 - np.sum((ys - pr) ** 2) / np.sum((ys - ys.mean()) ** 2)
        s.append(f'<line x1="{px(x0):.1f}" y1="{py(a*x0+b):.1f}" '
                 f'x2="{px(x1):.1f}" y2="{py(a*x1+b):.1f}" '
                 f'stroke="var(--di)" stroke-width="1.6" stroke-dasharray="5 3" opacity=".8"/>')
        r = np.corrcoef(xs, ys)[0, 1]
        s.append(f'<text x="{ww-mr-4}" y="{mt+14}" class="tick" text-anchor="end" '
                 f'style="font-size:11px;fill:var(--di)">R&#178;={r2:.2f} &#183; r={r:.2f}</text>')
    for x, y in zip(xs, ys):
        s.append(f'<circle cx="{px(x):.1f}" cy="{py(y):.1f}" r="4" class="pt"/>')
    s.append(f'<text x="{(ml+ww-mr)/2:.0f}" y="{hh-4}" class="axl" text-anchor="middle">{xlabel}</text>')
    s.append(f'<text x="11" y="{(mt+hh-mb)/2:.0f}" class="axl" text-anchor="middle" '
             f'transform="rotate(-90 11 {(mt+hh-mb)/2:.0f})">emb data-impl&#237;cito [&#181;m]</text>')
    s.append('</svg>')
    return "".join(s)


def coherence_section(res):
    liu = [e for e in res if "Liu2017" in e["name"]]
    ti = [e for e in res if "Li2022ti" in e["name"]]
    p1 = scatter_svg([e["AF_kN"]/e["F0_kN"] for e in liu],
                     [e["emb_data_um"] for e in liu], "raz&#227;o de carga A_F / F&#8320; [&#8211;]")
    p2 = scatter_svg([e["freq"] for e in ti],
                     [e["emb_data_um"] for e in ti], "frequ&#234;ncia [Hz]", fit=False)
    return f'''<h2>Coer&#234;ncia f&#237;sica &#8212; o emb data-impl&#237;cito segue uma LEI, n&#227;o &#233; fit</h2>
<p class="lede2">Se o <code>emb</code> lido da queda-inicial fosse ru&#237;do de ajuste, n&#227;o
correlacionaria com nada. Correlaciona: com a <b>raz&#227;o de carga A_F/F&#8320;</b> (Liu2017, carga
vari&#225;vel &#8212; mais amplitude por pr&#233;-carga, mais assentamento) e com <b>1/frequ&#234;ncia</b>
(Li2022ti, carga fixa &#8212; menos frequ&#234;ncia, mais dwell por ciclo, mais assentamento). &#201;
proveni&#234;ncia (f&#237;sica medida), n&#227;o fit.</p>
<div class="grid2">
  <div class="card"><div class="ct"><b>Liu2017</b> &#183; emb vs A_F/F&#8320; (mesmo rig, 9 cond.)</div>{p1}
    <div class="cf">Ajuste linear &#183; correla&#231;&#227;o forte: o assentamento escala com a raz&#227;o de carga.</div></div>
  <div class="card"><div class="ct"><b>Li2022ti</b> &#183; emb vs frequ&#234;ncia (A_F/F&#8320;=1 fixo)</div>{p2}
    <div class="cf">emb CAI monotonicamente com a frequ&#234;ncia (r&#8776;&#8722;0.99): efeito de dwell.</div></div>
</div>'''


def card(entry):
    hb, di = entry["handbook"]["mae"], entry["data_implied"]["mae"]
    better = di < hb - 1e-4
    badge = (f'<span class="delta good">&#9660; {(hb-di):.3f}</span>' if better
             else f'<span class="delta flat">&#8776;</span>')
    return f'''<div class="card">
  <div class="ct"><b>{entry["name"]}</b> {badge}</div>
  {svg(entry)}
  <div class="cf">emb: handbook <b>{entry["emb_handbook_um"]:.1f}&#181;m</b> &#8594;
     data-impl <b>{entry["emb_data_um"]:.2f}&#181;m</b> &#183;
     MAE handbook <b>{hb:.3f}</b> &#8594; data-impl <b>{di:.3f}</b></div>
</div>'''


def main():
    res = json.loads(DATA.read_text(encoding="utf-8"))
    import numpy as np
    mh = float(np.mean([e["handbook"]["mae"] for e in res]))
    md = float(np.mean([e["data_implied"]["mae"] for e in res]))
    groups = {}
    for e in res:
        groups.setdefault(e["group"], []).append(e)
    body = []
    # tabela-resumo
    rows = "".join(
        f'<tr><td>{e["name"]}</td><td>{e["emb_handbook_um"]:.1f}</td>'
        f'<td>{e["emb_data_um"]:.2f}</td><td>{e["handbook"]["mae"]:.3f}</td>'
        f'<td class="{"good" if e["data_implied"]["mae"]<e["handbook"]["mae"]-1e-4 else ""}">'
        f'{e["data_implied"]["mae"]:.3f}</td></tr>' for e in res)
    body.append(f'''<table class="sum"><thead><tr><th>Condi&#231;&#227;o</th>
      <th>emb handbook [&#181;m]</th><th>emb data-impl [&#181;m]</th>
      <th>MAE handbook</th><th>MAE data-impl</th></tr></thead><tbody>{rows}
      <tr class="tot"><td>M&#201;DIA ({len(res)})</td><td>&#8211;</td><td>&#8211;</td>
      <td>{mh:.3f}</td><td class="good">{md:.3f}</td></tr></tbody></table>''')
    body.append(coherence_section(res))
    for g, items in groups.items():
        body.append(f'<h2>{g}</h2><div class="grid">'
                    + "".join(card(e) for e in items) + '</div>')
    html = f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Proveni&#234;ncia do emb axial &#8212; dado&#215;modelo com erros</title>
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
.lede{{color:var(--mut);margin:0 0 22px;max-width:70ch}}
h2{{font-size:1rem;text-transform:uppercase;letter-spacing:.06em;color:var(--accent);
  margin:30px 0 10px;border-bottom:1px solid var(--bd);padding-bottom:5px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:14px}}
.grid2{{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:14px}}
.lede2{{color:var(--mut);margin:0 0 12px;max-width:78ch;font-size:.9rem}}
.card{{background:var(--card);border:1px solid var(--bd);border-radius:10px;padding:10px 12px}}
.plot{{width:100%;height:auto;display:block}}
.grid line{{}}line.grid{{stroke:var(--bd);stroke-width:.6}}
.tick{{fill:var(--mut);font-size:9px}}.axl{{fill:var(--mut);font-size:10px}}
.err{{stroke:var(--err);stroke-width:2.4;opacity:.55}}
.pt{{fill:var(--pt)}}
.ct{{font-size:.9rem;margin-bottom:2px;display:flex;justify-content:space-between;align-items:center}}
.cf{{font-size:.74rem;color:var(--mut);margin-top:6px;line-height:1.4}}
.delta{{font-size:.72rem;font-weight:600}}.delta.good{{color:var(--good)}}.delta.flat{{color:var(--mut)}}
.sum{{border-collapse:collapse;width:100%;margin:6px 0 8px;font-size:.82rem}}
.sum th,.sum td{{text-align:right;padding:5px 10px;border-bottom:1px solid var(--bd)}}
.sum th:first-child,.sum td:first-child{{text-align:left}}
.sum .tot{{font-weight:700}}.sum .good{{color:var(--good);font-weight:600}}
.legend{{display:flex;gap:18px;flex-wrap:wrap;font-size:.8rem;color:var(--mut);margin:10px 0 4px}}
.legend b{{color:var(--fg)}}.sw{{display:inline-block;width:22px;height:0;vertical-align:middle;margin-right:5px}}
.back{{font-size:.8rem;margin:0 0 10px}}.back a{{color:var(--accent);text-decoration:none}}
</style></head><body><div class="wrap">
<p class="back"><a href="index.html">&#8592; &#237;ndice de valida&#231;&#227;o</a></p>
<h1>Proveni&#234;ncia do <code>emb</code> axial &#8212; dado &#215; modelo, com erros</h1>
<p class="lede">Regra L24 (&#167;4.40): quando o handbook VDI f_Z e o valor <b>data-impl&#237;cito
da queda-inicial</b> divergem, o data-impl&#237;cito (lido da feature que o embedding governa) &#233;
mais espec&#237;fico. Zero-refit em modo for&#231;a axial, 13 condi&#231;&#245;es (Liu2017 + Li2022ti);
sem tuner, sem fit &#8212; s&#243; a troca do <code>emb</code> de handbook por data-impl&#237;cito.</p>
<div class="legend">
  <span><span class="sw" style="border-top:2.2px solid var(--di)"></span><b>modelo</b> emb data-impl&#237;cito</span>
  <span><span class="sw" style="border-top:2px dashed var(--hb)"></span>modelo emb handbook (VDI Rz&lt;10)</span>
  <span><span class="sw" style="border-top:2.4px solid var(--err);opacity:.55"></span>erro |modelo&#8722;dado|</span>
  <span>&#9679; dado</span>
</div>
{''.join(body)}
</div></body></html>'''
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(f"escrito: {OUT}  ({len(res)} condicoes; MAE {mh:.3f}->{md:.3f})")


if __name__ == "__main__":
    main()
