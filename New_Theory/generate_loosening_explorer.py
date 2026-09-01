"""EXPLORADOR de curvas de loosening — pagina UNICA e interativa.

Diretiva do professor: "uma interface onde eu veja as curvas de loosening dos
artigos, as que o software gera, e o erro entre elas, tudo em uma unica pagina".

Le o report_data.json CANONICO (harness da galeria — L1, nunca recomputar de
label) e gera validation_html/loosening_explorer.html: pagina self-contained
(JSON embutido, JS vanilla, sem CDN) com as 82 curvas:
  - cada card: dado do artigo (pontos+linha fina) x modelo (linha grossa) +
    barras de erro |modelo-dado| nos pontos do dado + badge de MAE;
  - filtros por familia (transversal/axial) e por fonte (chips com contagem),
    ordenacao (erro desc/asc, fonte, n_max), stats ao vivo do filtro;
  - clique no card -> detalhe com plot grande + SUBPLOT DO ERRO eps(N) =
    modelo-dado (linha zero), metricas (MAE, MAE/RMSE interp, erro max @ ciclo)
    e link para a pagina standalone do caso.

Run: python New_Theory/generate_loosening_explorer.py
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "New_Theory/report_data.json"
OUT = ROOT / "New_Theory/validation_html/loosening_explorer.html"

AXIAL_SRC = {"LIU_2017_P0", "LIU_2017_AF", "LI_2022TI"}
NICE = {
    "LIU_2025": "Liu 2025 (M16)", "YANG_2019": "Yang 2019 (M10)",
    "ROUSSEAU_2025": "Rousseau aço", "ROUSSEAU_HDPE": "Rousseau HDPE",
    "KARLSEN_2022": "Karlsen (M30/M42)", "LU_2024": "Lu 2024 (M8)",
    "ICMEZ_2025": "Içmez/Demir (M12)", "BAUER_2024": "Bauer 2024",
    "ZHANG_2006": "Zhang 2006 (M12)", "LIU_2022": "Liu 2022 fig5",
    "LIU_2022_RET": "Liu 2022 reaperto", "LIU_2017_P0": "Liu 2017 F0-sweep",
    "LIU_2017_AF": "Liu 2017 A_F-sweep", "LI_2022TI": "Li 2022 Ti ×freq",
}


def slim(g):
    fam = g.get("family") or ("axial" if g["source"] in AXIAL_SRC else "transverse")
    return dict(csv=g["csv"], source=g["source"], label=g.get("label", ""),
                fam=fam, mae=round(g["mae"], 4),
                mi=round(g.get("mae_interp", g["mae"]), 4),
                mx=round(g.get("maxerr_interp", 0.0), 4),
                mxa=g.get("maxerr_at", 0), amp=g.get("amp_mm", 0),
                n=g["n_max"], d=g["data"], m=g["model"])


def main():
    gallery = json.loads(DATA.read_text(encoding="utf-8"))["gallery"]
    entries = [slim(g) for g in gallery]
    payload = json.dumps(dict(entries=entries, nice=NICE),
                         ensure_ascii=False, separators=(",", ":"))
    html = HTML.replace("__PAYLOAD__", payload.replace("</", "<\\/"))
    OUT.write_text(html, encoding="utf-8")
    import statistics
    maes = [e["mae"] for e in entries]
    print(f"escrito: {OUT}")
    print(f"  {len(entries)} curvas · MAE médio {statistics.mean(maes):.3f} · "
          f"mediana {statistics.median(maes):.3f} · máx {max(maes):.3f}")


HTML = r"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Explorador de loosening — dado × modelo × erro</title>
<style>
:root{--bg:#faf9f7;--fg:#1c1a17;--mut:#6b655c;--card:#fff;--bd:#e6e1d8;
  --di:#2f6f8f;--err:#c0392b;--pt:#1c1a17;--good:#1a7a4c;--warn:#b3452c;--accent:#2f6f8f;
  --chipbg:#efece6;--chipon:#2f6f8f;--chipfg:#fff;--ov:rgba(20,18,14,.55)}
@media (prefers-color-scheme:dark){:root{--bg:#16140f;--fg:#ece7de;--mut:#9a938a;
  --card:#211e18;--bd:#332e26;--di:#6bb6d6;--err:#e8776b;--pt:#ece7de;--good:#5fd39a;
  --warn:#e8936b;--accent:#6bb6d6;--chipbg:#2a2620;--chipon:#6bb6d6;--chipfg:#16140f;--ov:rgba(0,0,0,.6)}}
:root[data-theme=dark]{--bg:#16140f;--fg:#ece7de;--mut:#9a938a;--card:#211e18;--bd:#332e26;
  --di:#6bb6d6;--err:#e8776b;--pt:#ece7de;--good:#5fd39a;--warn:#e8936b;--accent:#6bb6d6;
  --chipbg:#2a2620;--chipon:#6bb6d6;--chipfg:#16140f;--ov:rgba(0,0,0,.6)}
:root[data-theme=light]{--bg:#faf9f7;--fg:#1c1a17;--mut:#6b655c;--card:#fff;--bd:#e6e1d8;
  --di:#2f6f8f;--err:#c0392b;--pt:#1c1a17;--good:#1a7a4c;--warn:#b3452c;--accent:#2f6f8f;
  --chipbg:#efece6;--chipon:#2f6f8f;--chipfg:#fff;--ov:rgba(20,18,14,.55)}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
  font:15px/1.5 -apple-system,"Segoe UI",Roboto,sans-serif;padding-bottom:70px}
.wrap{max-width:1280px;margin:0 auto;padding:24px 20px 0}
.back{font-size:.8rem;margin:0 0 8px}.back a{color:var(--accent);text-decoration:none}
h1{font-size:1.45rem;margin:0 0 2px;letter-spacing:-.01em}
.lede{color:var(--mut);margin:0 0 14px;max-width:78ch;font-size:.92rem}
.bar{position:sticky;top:0;z-index:5;background:var(--bg);border-bottom:1px solid var(--bd);
  padding:10px 0 8px;margin-bottom:14px}
.row{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-bottom:6px}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{border:1px solid var(--bd);background:var(--chipbg);color:var(--fg);border-radius:999px;
  padding:3px 11px;font-size:.78rem;cursor:pointer;user-select:none}
.chip.on{background:var(--chipon);color:var(--chipfg);border-color:var(--chipon)}
.chip:focus-visible{outline:2px solid var(--accent);outline-offset:1px}
select{background:var(--card);color:var(--fg);border:1px solid var(--bd);border-radius:8px;
  padding:4px 8px;font-size:.8rem}
.stats{font-family:Consolas,monospace;font-size:.78rem;color:var(--mut)}
.stats b{color:var(--fg)}
.legend{display:flex;gap:16px;flex-wrap:wrap;font-size:.76rem;color:var(--mut)}
.legend b{color:var(--fg)}.sw{display:inline-block;width:20px;height:0;vertical-align:middle;margin-right:4px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:12px}
.card{background:var(--card);border:1px solid var(--bd);border-radius:10px;padding:9px 11px;
  cursor:pointer;transition:border-color .12s}
.card:hover{border-color:var(--accent)}
.card:focus-visible{outline:2px solid var(--accent);outline-offset:1px}
.ct{display:flex;justify-content:space-between;align-items:baseline;gap:6px;font-size:.8rem;margin-bottom:2px}
.ct .nm{font-weight:650;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.badge{font-family:Consolas,monospace;font-size:.72rem;font-weight:700;white-space:nowrap}
.badge.g{color:var(--good)}.badge.w{color:var(--warn)}
.cf{font-size:.7rem;color:var(--mut);margin-top:4px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
svg{display:block;width:100%;height:auto}
.gl{stroke:var(--bd);stroke-width:.6}
.tick{fill:var(--mut);font-size:9px}.axl{fill:var(--mut);font-size:10px}
.errb{stroke:var(--err);stroke-width:2.2;opacity:.5}
.dline{stroke:var(--pt);stroke-width:1.2;fill:none;opacity:.85}
.dpt{fill:var(--pt)}
.mline{stroke:var(--di);stroke-width:2.2;fill:none}
.eline{stroke:var(--err);stroke-width:1.8;fill:none}
.zline{stroke:var(--mut);stroke-width:.8;stroke-dasharray:4 3}
dialog{border:1px solid var(--bd);border-radius:14px;background:var(--card);color:var(--fg);
  max-width:880px;width:calc(100vw - 40px);padding:18px 20px}
dialog::backdrop{background:var(--ov)}
.mhead{display:flex;justify-content:space-between;gap:10px;align-items:baseline;margin-bottom:4px}
.mhead h2{font-size:1.05rem;margin:0}
.mclose{background:none;border:1px solid var(--bd);border-radius:8px;color:var(--fg);
  cursor:pointer;font-size:.8rem;padding:3px 10px}
.mlabel{font-size:.78rem;color:var(--mut);margin:0 0 10px;line-height:1.45}
.mtab{border-collapse:collapse;font-family:Consolas,monospace;font-size:.78rem;margin:10px 0 4px}
.mtab td{padding:3px 14px 3px 0;border-bottom:1px solid var(--bd)}
.mtab td:first-child{color:var(--mut)}
.mlink{font-size:.8rem}.mlink a{color:var(--accent)}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
</style></head><body>
<div class="wrap">
<p class="back"><a href="index.html">&#8592; índice de validação</a></p>
<h1>Explorador de loosening — artigo × software × erro</h1>
<p class="lede">Todas as curvas de perda de pré-carga da validação numa página:
o dado digitalizado do artigo, a curva que o engine V2 gera na configuração
per-rig declarada (harness canônico, <code>report_data.json</code>), e o erro
entre elas. Clique numa curva para o detalhe com o subplot do erro ε(N).</p>
<div class="bar">
  <div class="row">
    <div class="chips" id="famChips"></div>
    <select id="sortSel" aria-label="ordenar">
      <option value="mae_desc">erro: maior → menor</option>
      <option value="mae_asc">erro: menor → maior</option>
      <option value="src">por fonte</option>
      <option value="n">por nº de ciclos</option>
    </select>
    <span class="stats" id="stats"></span>
  </div>
  <div class="row"><div class="chips" id="srcChips"></div></div>
  <div class="row legend">
    <span><span class="sw" style="border-top:2.2px solid var(--di)"></span><b>modelo</b> (software)</span>
    <span><span class="sw" style="border-top:1.4px solid var(--pt)"></span>dado do artigo</span>
    <span><span class="sw" style="border-top:2.2px solid var(--err);opacity:.5"></span>erro |modelo−dado|</span>
  </div>
</div>
<div class="grid" id="grid"></div>
</div>
<dialog id="dlg">
  <div class="mhead"><h2 id="dTitle"></h2>
    <button class="mclose" id="dClose">fechar ✕</button></div>
  <p class="mlabel" id="dLabel"></p>
  <div id="dPlot"></div>
  <div id="dErr"></div>
  <table class="mtab" id="dTab"></table>
  <p class="mlink" id="dLink"></p>
</dialog>
<script type="application/json" id="payload">__PAYLOAD__</script>
<script>
"use strict";
const P = JSON.parse(document.getElementById("payload").textContent);
const E = P.entries, NICE = P.nice;
const interp = (xs, ys, x) => {
  if (x <= xs[0]) return ys[0];
  if (x >= xs[xs.length-1]) return ys[ys.length-1];
  let i = 1; while (xs[i] < x) i++;
  const t = (x - xs[i-1]) / (xs[i] - xs[i-1] || 1);
  return ys[i-1] + t * (ys[i] - ys[i-1]);
};
const S = { fam: "all", srcs: new Set(), sort: "mae_desc" };

function plotSVG(e, W, H, opts) {
  const ML = 46, MR = 12, MT = 12, MB = 34;
  const axial = e.fam === "axial";
  const xmax = Math.max(e.n, e.d.x[e.d.x.length-1]);
  const xmin = axial ? Math.max(1, e.d.x.find(v => v > 0) || 1) : 0;
  const lx = axial
    ? x => ML + (Math.log10(Math.max(x, xmin)) - Math.log10(xmin)) /
           (Math.log10(xmax) - Math.log10(xmin) || 1) * (W - ML - MR)
    : x => ML + (x - xmin) / (xmax - xmin || 1) * (W - ML - MR);
  const ymax = 1.08;
  const ly = y => MT + (1 - Math.max(y, 0) / ymax) * (H - MT - MB);
  let s = `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" role="img">`;
  for (const yv of [0, .25, .5, .75, 1]) {
    const yy = ly(yv);
    s += `<line class="gl" x1="${ML}" y1="${yy}" x2="${W-MR}" y2="${yy}"/>` +
         `<text class="tick" x="${ML-5}" y="${yy+3}" text-anchor="end">${yv.toFixed(2)}</text>`;
  }
  if (axial) {
    for (let ex = Math.ceil(Math.log10(xmin)); ex <= Math.log10(xmax); ex++) {
      const xx = lx(10**ex);
      s += `<line class="gl" x1="${xx}" y1="${MT}" x2="${xx}" y2="${H-MB}"/>` +
           `<text class="tick" x="${xx}" y="${H-MB+13}" text-anchor="middle">1e${ex}</text>`;
    }
  } else {
    for (const f of [.25, .5, .75, 1]) {
      const xx = lx(xmax*f);
      s += `<line class="gl" x1="${xx}" y1="${MT}" x2="${xx}" y2="${H-MB}"/>` +
           `<text class="tick" x="${xx}" y="${H-MB+13}" text-anchor="middle">${Math.round(xmax*f)}</text>`;
    }
  }
  // barras de erro nos pontos do dado
  for (let i = 0; i < e.d.x.length; i++) {
    const ym = interp(e.m.x, e.m.y, e.d.x[i]);
    s += `<line class="errb" x1="${lx(e.d.x[i]).toFixed(1)}" y1="${ly(e.d.y[i]).toFixed(1)}"` +
         ` x2="${lx(e.d.x[i]).toFixed(1)}" y2="${ly(ym).toFixed(1)}"/>`;
  }
  const pl = (xs, ys) => xs.map((x,i) => `${lx(x).toFixed(1)},${ly(ys[i]).toFixed(1)}`).join(" ");
  s += `<polyline class="mline" points="${pl(e.m.x, e.m.y)}"/>`;
  s += `<polyline class="dline" points="${pl(e.d.x, e.d.y)}"/>`;
  for (let i = 0; i < e.d.x.length; i++)
    s += `<circle class="dpt" cx="${lx(e.d.x[i]).toFixed(1)}" cy="${ly(e.d.y[i]).toFixed(1)}" r="${opts.big?3:2.4}"/>`;
  s += `<text class="axl" x="${(ML+W-MR)/2}" y="${H-3}" text-anchor="middle">ciclos N${axial?" (log)":""}</text>`;
  s += `<text class="axl" x="11" y="${(MT+H-MB)/2}" text-anchor="middle"` +
       ` transform="rotate(-90 11 ${(MT+H-MB)/2})">F / F&#8320; [&#8211;]</text></svg>`;
  return s;
}

function errSVG(e, W, H) {
  const ML = 46, MR = 12, MT = 10, MB = 30;
  const axial = e.fam === "axial";
  const xmax = Math.max(e.n, e.d.x[e.d.x.length-1]);
  const xmin = axial ? Math.max(1, e.d.x.find(v => v > 0) || 1) : 0;
  const lx = axial
    ? x => ML + (Math.log10(Math.max(x, xmin)) - Math.log10(xmin)) /
           (Math.log10(xmax) - Math.log10(xmin) || 1) * (W - ML - MR)
    : x => ML + (x - xmin) / (xmax - xmin || 1) * (W - ML - MR);
  const eps = e.d.x.map((x,i) => interp(e.m.x, e.m.y, x) - e.d.y[i]);
  const em = Math.max(...eps.map(Math.abs), .02) * 1.2;
  const ly = v => MT + (1 - (v + em) / (2*em)) * (H - MT - MB);
  let s = `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" role="img">`;
  s += `<line class="zline" x1="${ML}" y1="${ly(0)}" x2="${W-MR}" y2="${ly(0)}"/>`;
  for (const v of [-em/1.2, 0, em/1.2])
    s += `<text class="tick" x="${ML-5}" y="${ly(v)+3}" text-anchor="end">${v>0?"+":""}${v.toFixed(2)}</text>`;
  s += `<polyline class="eline" points="${e.d.x.map((x,i)=>`${lx(x).toFixed(1)},${ly(eps[i]).toFixed(1)}`).join(" ")}"/>`;
  for (let i = 0; i < e.d.x.length; i++)
    s += `<circle cx="${lx(e.d.x[i]).toFixed(1)}" cy="${ly(eps[i]).toFixed(1)}" r="2.2" fill="var(--err)"/>`;
  s += `<text class="axl" x="${(ML+W-MR)/2}" y="${H-2}" text-anchor="middle">erro &#949;(N) = modelo &#8722; dado</text></svg>`;
  return s;
}

function visible() {
  let v = E.filter(e => (S.fam === "all" || e.fam === S.fam) &&
                        (S.srcs.size === 0 || S.srcs.has(e.source)));
  const k = S.sort;
  if (k === "mae_desc") v.sort((a,b) => b.mae - a.mae);
  else if (k === "mae_asc") v.sort((a,b) => a.mae - b.mae);
  else if (k === "src") v.sort((a,b) => a.source.localeCompare(b.source) || b.mae - a.mae);
  else v.sort((a,b) => b.n - a.n);
  return v;
}

function render() {
  const v = visible();
  const grid = document.getElementById("grid");
  grid.innerHTML = v.map((e,i) => {
    const cls = e.mae <= 0.1 ? "g" : "w";
    return `<div class="card" tabindex="0" data-i="${E.indexOf(e)}" role="button"
      aria-label="${e.csv}">
      <div class="ct"><span class="nm" title="${e.csv}">${e.csv}</span>
        <span class="badge ${cls}">MAE ${e.mae.toFixed(3)}</span></div>
      ${plotSVG(e, 380, 240, {big:false})}
      <div class="cf">${NICE[e.source]||e.source} · ${e.fam === "axial" ? "axial" : "transversal"}` +
      `${e.amp ? " · amp " + e.amp + " mm" : ""} · N=${e.n.toLocaleString("pt-BR")}</div></div>`;
  }).join("");
  const maes = v.map(e => e.mae).sort((a,b) => a-b);
  const mean = maes.reduce((a,b) => a+b, 0) / (maes.length || 1);
  document.getElementById("stats").innerHTML = maes.length
    ? `<b>${maes.length}</b> curvas · MAE médio <b>${mean.toFixed(3)}</b> · ` +
      `mediana <b>${maes[Math.floor(maes.length/2)].toFixed(3)}</b> · máx <b>${maes[maes.length-1].toFixed(3)}</b>`
    : "0 curvas";
  grid.querySelectorAll(".card").forEach(c => {
    c.addEventListener("click", () => openDetail(+c.dataset.i));
    c.addEventListener("keydown", ev => { if (ev.key === "Enter") openDetail(+c.dataset.i); });
  });
}

function openDetail(i) {
  const e = E[i];
  document.getElementById("dTitle").textContent = e.csv;
  document.getElementById("dLabel").textContent =
    (NICE[e.source]||e.source) + " · config: " + (e.label || "(galeria)");
  document.getElementById("dPlot").innerHTML = plotSVG(e, 820, 380, {big:true});
  document.getElementById("dErr").innerHTML = errSVG(e, 820, 150);
  document.getElementById("dTab").innerHTML =
    `<tr><td>MAE (pontos do dado)</td><td>${e.mae.toFixed(4)}</td></tr>` +
    `<tr><td>MAE interp (PCHIP denso)</td><td>${e.mi.toFixed(4)}</td></tr>` +
    `<tr><td>erro máx interp</td><td>${e.mx.toFixed(4)} @ ciclo ${Math.round(e.mxa).toLocaleString("pt-BR")}</td></tr>` +
    `<tr><td>família / amplitude</td><td>${e.fam === "axial" ? "axial (modo força)" : "transversal (disp)"}` +
    `${e.amp ? " · " + e.amp + " mm" : ""}</td></tr>`;
  document.getElementById("dLink").innerHTML =
    `<a href="${e.csv}.html">abrir página standalone do caso →</a>`;
  document.getElementById("dlg").showModal();
}

// chips
const fams = [["all","todas"],["transverse","transversal"],["axial","axial"]];
const famBox = document.getElementById("famChips");
famBox.innerHTML = fams.map(([k,lb]) =>
  `<span class="chip${k==='all'?' on':''}" data-f="${k}" tabindex="0" role="button">${lb}</span>`).join("");
famBox.querySelectorAll(".chip").forEach(ch => {
  const act = () => { S.fam = ch.dataset.f;
    famBox.querySelectorAll(".chip").forEach(x => x.classList.toggle("on", x === ch));
    render(); };
  ch.addEventListener("click", act);
  ch.addEventListener("keydown", ev => { if (ev.key === "Enter") act(); });
});
const counts = {};
E.forEach(e => counts[e.source] = (counts[e.source]||0) + 1);
const srcBox = document.getElementById("srcChips");
srcBox.innerHTML = Object.keys(counts).sort().map(s =>
  `<span class="chip" data-s="${s}" tabindex="0" role="button">${NICE[s]||s} (${counts[s]})</span>`).join("");
srcBox.querySelectorAll(".chip").forEach(ch => {
  const act = () => { const s = ch.dataset.s;
    if (S.srcs.has(s)) S.srcs.delete(s); else S.srcs.add(s);
    ch.classList.toggle("on"); render(); };
  ch.addEventListener("click", act);
  ch.addEventListener("keydown", ev => { if (ev.key === "Enter") act(); });
});
document.getElementById("sortSel").addEventListener("change", ev => { S.sort = ev.target.value; render(); });
document.getElementById("dClose").addEventListener("click", () => document.getElementById("dlg").close());
document.getElementById("dlg").addEventListener("click", ev => {
  if (ev.target === ev.currentTarget) ev.currentTarget.close();
});
render();
</script></body></html>
"""


if __name__ == "__main__":
    main()
