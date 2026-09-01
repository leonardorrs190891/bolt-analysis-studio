"""Galeria dos GRAFICOS DE LOOSENING (theta) — rotacao da porca, dado x modelo.

O canal theta nunca tinha sido PLOTADO: o confronto §4.23 (theta_confront.py)
so imprimiu no console. Esta galeria reusa o harness canonico por IMPORT (L1 —
nunca reconstruir config) e renderiza as 6 curvas theta(N) medidas (Rousseau
Figs 4/5, theta_csv/, extracao vetorial 160 pts) contra o theta_loose do engine,
com barras de erro |modelo-dado| e a tabela do confronto (theta_fim, share
rotacional, gates G-T1/G-T2 do §4.23).

Honestidade: o deficit conhecido do canal theta fica VISIVEL — o aco colapsante
mede ~3.3x mais theta do que a perda de preload explica via helice (free-spin
pos-arresto, §4.23); a galeria mostra, nao esconde.

Run: python New_Theory/generate_theta_gallery.py   (~1-2 min)
Escreve: theta_gallery.json + validation_html/theta_loosening.html
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "New_Theory"))

import theta_confront as tc  # noqa: E402  (harness canonico §4.23)

OUT_JSON = ROOT / "New_Theory/theta_gallery.json"
OUT_HTML = ROOT / "New_Theory/validation_html/theta_loosening.html"

W, H = 400, 270
ML, MR, MT, MB = 52, 14, 16, 40


def compute():
    results = []
    for matname, runs in [("steel", [("t10",), ("t12",), ("t14",)]),
                          ("hdpe", tc.HDPE_CASES)]:
        for entry in runs:
            t = entry[0]
            if matname == "steel":
                th, r, F0, geom, jm, cum, nmax = tc.run_steel(
                    f"rousseau2025_steel_{t}")
            else:
                th, r, F0, geom, jm, cum, nmax = tc.run_hdpe(*entry)
            cyc_m, deg_m = tc.theta_meas(matname, t)
            keep = cyc_m <= nmax
            cyc_m, deg_m = cyc_m[keep], deg_m[keep]
            mi = np.interp(cyc_m, np.arange(nmax + 1), th)
            mae = float(np.mean(np.abs(mi - deg_m)))
            tot = sum(abs(v) for v in cum.values()) or 1.0
            share_rot = abs(cum.get("rotational_loosening", 0.0)) / tot
            frac_data, k_eff = tc.helix_rot_fraction(
                float(deg_m[-1]), F0, float(np.interp(cyc_m[-1],
                np.arange(nmax + 1), r)), geom, jm)
            # grade coarse do modelo p/ plot
            gx = np.unique(np.linspace(0, nmax, 120).astype(int))
            results.append(dict(
                name=f"{matname} {t}", material=matname, t=t, n_max=int(nmax),
                F0_kN=F0 / 1e3, mae_deg=mae,
                theta_fim_model=float(th[-1]), theta_fim_data=float(deg_m[-1]),
                share_rot_model=share_rot, helix_frac_data=float(frac_data),
                data=dict(x=cyc_m.tolist(), y=deg_m.tolist()),
                model=dict(x=gx.tolist(), y=[float(th[i]) for i in gx])))
            print(f"[{matname}_{t}] theta_fim mod {th[-1]:6.2f} vs dado "
                  f"{deg_m[-1]:6.2f} deg | MAE {mae:.2f} deg | "
                  f"share_rot {share_rot:.0%}", flush=True)
    OUT_JSON.write_text(json.dumps(results, ensure_ascii=False),
                        encoding="utf-8")
    return results


def svg(e):
    dx, dy = np.array(e["data"]["x"]), np.array(e["data"]["y"])
    mx, my = np.array(e["model"]["x"]), np.array(e["model"]["y"])
    ymax = max(float(dy.max()), float(my.max()), 1.0) * 1.12
    xmax = max(e["n_max"], float(dx.max()))

    def px(x): return ML + x / xmax * (W - ML - MR)
    def py(y): return MT + (1 - max(y, 0.0) / ymax) * (H - MT - MB)
    s = [f'<svg viewBox="0 0 {W} {H}" class="plot" xmlns="http://www.w3.org/2000/svg">']
    for i in range(5):
        yv = ymax * i / 4
        yy = py(yv)
        s.append(f'<line x1="{ML}" y1="{yy:.1f}" x2="{W-MR}" y2="{yy:.1f}" class="grid"/>')
        s.append(f'<text x="{ML-6}" y="{yy+3:.1f}" class="tick" text-anchor="end">{yv:.1f}</text>')
    for fx in (0.25, 0.5, 0.75, 1.0):
        xx = px(xmax * fx)
        s.append(f'<line x1="{xx:.1f}" y1="{MT}" x2="{xx:.1f}" y2="{H-MB}" class="grid"/>')
        s.append(f'<text x="{xx:.1f}" y="{H-MB+14}" class="tick" text-anchor="middle">{int(xmax*fx)}</text>')
    # barras de erro em ~14 posicoes amostradas do dado
    idx = np.unique(np.linspace(0, len(dx) - 1, 14).astype(int))
    mi = np.interp(dx, mx, my)
    for i in idx:
        s.append(f'<line x1="{px(dx[i]):.1f}" y1="{py(dy[i]):.1f}" '
                 f'x2="{px(dx[i]):.1f}" y2="{py(mi[i]):.1f}" class="err"/>')
    # dado denso = linha fina; modelo = linha grossa
    dpts = " ".join(f"{px(x):.1f},{py(y):.1f}" for x, y in zip(dx, dy))
    s.append(f'<polyline points="{dpts}" fill="none" stroke="var(--pt)" '
             f'stroke-width="1.3" opacity="0.9"/>')
    mpts = " ".join(f"{px(x):.1f},{py(y):.1f}" for x, y in zip(mx, my))
    s.append(f'<polyline points="{mpts}" fill="none" stroke="var(--di)" stroke-width="2.2"/>')
    s.append(f'<circle cx="{px(dx[-1]):.1f}" cy="{py(dy[-1]):.1f}" r="3" class="ptdot"/>')
    s.append(f'<text x="{(ML+W-MR)/2:.0f}" y="{H-4}" class="axl" text-anchor="middle">ciclos N</text>')
    s.append(f'<text x="12" y="{(MT+H-MB)/2:.0f}" class="axl" text-anchor="middle" '
             f'transform="rotate(-90 12 {(MT+H-MB)/2:.0f})">&#952; rota&#231;&#227;o da porca [&#176;]</text>')
    s.append('</svg>')
    return "".join(s)


def card(e):
    fac = e["theta_fim_model"] / max(e["theta_fim_data"], 1e-3)
    ok = 1 / 3 <= fac <= 3 or e["theta_fim_data"] < 1.0
    badge = (f'<span class="delta good">fator {fac:.2f}</span>' if ok
             else f'<span class="delta bad">fator {fac:.2f}</span>')
    return f'''<div class="card">
  <div class="ct"><b>{e["name"]}</b> {badge}</div>
  {svg(e)}
  <div class="cf">&#952;_fim: modelo <b>{e["theta_fim_model"]:.1f}&#176;</b> vs dado
    <b>{e["theta_fim_data"]:.1f}&#176;</b> &#183; MAE {e["mae_deg"]:.2f}&#176; &#183;
    share rotacional (modelo) {e["share_rot_model"]:.0%} &#183;
    h&#233;lice&#183;&#952;_dado/perda {e["helix_frac_data"]:.2f}</div>
</div>'''


def render(res):
    rows = "".join(
        f'<tr><td>{e["name"]}</td><td>{e["theta_fim_model"]:.1f}</td>'
        f'<td>{e["theta_fim_data"]:.1f}</td><td>{e["mae_deg"]:.2f}</td>'
        f'<td>{e["share_rot_model"]:.0%}</td><td>{e["helix_frac_data"]:.2f}</td></tr>'
        for e in res)
    groups = {}
    for e in res:
        groups.setdefault(e["material"], []).append(e)
    body = []
    for mname, items in (("steel", groups.get("steel", [])),
                         ("hdpe", groups.get("hdpe", []))):
        title = "A&#231;o (Rousseau fig 5)" if mname == "steel" else "HDPE (Rousseau fig 4)"
        body.append(f'<h2>{title} &#183; t10 / t12 / t14</h2><div class="grid">'
                    + "".join(card(e) for e in items) + '</div>')
    html = f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Gr&#225;ficos de loosening &#8212; rota&#231;&#227;o &#952; da porca, dado&#215;modelo</title>
<style>
:root{{--bg:#faf9f7;--fg:#1c1a17;--mut:#6b655c;--card:#fff;--bd:#e6e1d8;
  --di:#2f6f8f;--err:#c0392b;--pt:#1c1a17;--good:#1a7a4c;--bad:#b3452c;--accent:#2f6f8f}}
@media (prefers-color-scheme:dark){{:root{{--bg:#16140f;--fg:#ece7de;--mut:#9a938a;
  --card:#211e18;--bd:#332e26;--di:#6bb6d6;--err:#e8776b;--pt:#ece7de;--good:#5fd39a;--bad:#e8936b}}}}
:root[data-theme=dark]{{--bg:#16140f;--fg:#ece7de;--mut:#9a938a;--card:#211e18;--bd:#332e26;
  --di:#6bb6d6;--err:#e8776b;--pt:#ece7de;--good:#5fd39a;--bad:#e8936b}}
:root[data-theme=light]{{--bg:#faf9f7;--fg:#1c1a17;--mut:#6b655c;--card:#fff;--bd:#e6e1d8;
  --di:#2f6f8f;--err:#c0392b;--pt:#1c1a17;--good:#1a7a4c;--bad:#b3452c}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--fg);
  font:15px/1.55 -apple-system,Segoe UI,Roboto,sans-serif;padding:28px 20px 60px}}
.wrap{{max-width:1180px;margin:0 auto}}
.back{{font-size:.8rem;margin:0 0 10px}}.back a{{color:var(--accent);text-decoration:none}}
h1{{font-size:1.5rem;margin:0 0 4px;letter-spacing:-.01em}}
.lede{{color:var(--mut);margin:0 0 8px;max-width:74ch}}
.note{{background:var(--card);border:1px solid var(--bd);border-left:3px solid var(--accent);
  border-radius:8px;padding:10px 14px;margin:12px 0 20px;font-size:.86rem;max-width:80ch}}
h2{{font-size:1rem;text-transform:uppercase;letter-spacing:.06em;color:var(--accent);
  margin:28px 0 10px;border-bottom:1px solid var(--bd);padding-bottom:5px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:14px}}
.card{{background:var(--card);border:1px solid var(--bd);border-radius:10px;padding:10px 12px}}
.plot{{width:100%;height:auto;display:block}}
line.grid{{stroke:var(--bd);stroke-width:.6}}
.tick{{fill:var(--mut);font-size:9px}}.axl{{fill:var(--mut);font-size:10px}}
.err{{stroke:var(--err);stroke-width:2.4;opacity:.5}}
.ptdot{{fill:var(--pt)}}
.ct{{font-size:.9rem;margin-bottom:2px;display:flex;justify-content:space-between;align-items:center}}
.cf{{font-size:.74rem;color:var(--mut);margin-top:6px;line-height:1.45}}
.delta{{font-size:.72rem;font-weight:600}}.delta.good{{color:var(--good)}}.delta.bad{{color:var(--bad)}}
.sum{{border-collapse:collapse;width:100%;margin:6px 0 8px;font-size:.84rem}}
.sum th,.sum td{{text-align:right;padding:5px 12px;border-bottom:1px solid var(--bd)}}
.sum th:first-child,.sum td:first-child{{text-align:left}}
.legend{{display:flex;gap:18px;flex-wrap:wrap;font-size:.8rem;color:var(--mut);margin:10px 0 4px}}
.legend b{{color:var(--fg)}}.sw{{display:inline-block;width:22px;height:0;vertical-align:middle;margin-right:5px}}
</style></head><body><div class="wrap">
<p class="back"><a href="index.html">&#8592; &#237;ndice de valida&#231;&#227;o</a></p>
<h1>Gr&#225;ficos de loosening &#8212; rota&#231;&#227;o &#952; da porca, dado &#215; modelo</h1>
<p class="lede">O canal &#952; do engine (<code>state.theta_loose</code>) confrontado
ZERO-REFIT com as 6 curvas &#952;(N) medidas (Rousseau 2025 Figs 4/5, extra&#231;&#227;o
vetorial 160 pts/curva, <code>theta_csv/</code>). O dado &#952; nunca entrou em
calibra&#231;&#227;o &#8212; configs = as ADOTADAS da galeria (&#167;4.23).</p>
<div class="note"><b>Honestidade do canal &#952; (&#167;4.23):</b> o a&#231;o colapsante mede
~3.3&#215; mais &#952; do que a perda de pr&#233;-carga explica via h&#233;lice
(<code>dF&#8320;=k_eff&#183;(p/2&#960;)&#183;&#952;</code>) &#8212; rota&#231;&#227;o livre
p&#243;s-arresto (free-spin) que N&#195;O drena preload. O modelo com free-spin default-OFF
sub-prediz &#952; nesses casos por constru&#231;&#227;o; a coluna
&#8220;h&#233;lice&#183;&#952;_dado/perda&#8221; quantifica isso NO DADO. Gates do confronto:
G-T1 (ordem t10&gt;t12&gt;t14) e G-T2 (fator&#8804;3 / t14&#8804;4&#176;).</div>
<div class="legend">
  <span><span class="sw" style="border-top:2.2px solid var(--di)"></span><b>modelo</b> &#952;_loose</span>
  <span><span class="sw" style="border-top:1.3px solid var(--pt)"></span>dado &#952;(N) (vetorial, 160 pts)</span>
  <span><span class="sw" style="border-top:2.4px solid var(--err);opacity:.5"></span>erro |modelo&#8722;dado| (amostrado)</span>
</div>
<table class="sum"><thead><tr><th>caso</th><th>&#952;_fim modelo [&#176;]</th>
<th>&#952;_fim dado [&#176;]</th><th>MAE [&#176;]</th><th>share rot. (modelo)</th>
<th>h&#233;lice&#183;&#952;_dado/perda</th></tr></thead><tbody>{rows}</tbody></table>
{''.join(body)}
<p class="lede" style="margin-top:18px;font-size:.8rem">Dado &#952; adicional da biblioteca
(&#226;ncoras, outros observ&#225;veis): yang2011 &#952;-por-preload, li2021 rota&#231;&#227;o
&#215;amplitude/freq, sakai2011 axial &#8212; em <code>anchors_csv/</code>; n&#227;o s&#227;o
&#952;(N) e ficam fora desta galeria.</p>
</div></body></html>'''
    OUT_HTML.write_text(html, encoding="utf-8")
    print(f"escrito: {OUT_HTML}")


if __name__ == "__main__":
    render(compute())
