"""Indice HTML do DATABASE de curvas (pedido do professor 2026-07-08:
"digitalizar todas as curvas para termos um database"). Varre dinamicamente as
pastas de CSV da curve_library (digitized/extracted + as novas anchors/theta/
loops) e gera um catalogo navegavel com contagens, spans e proveniencia.

Run: python New_Theory/generate_database_html.py
Saida: New_Theory/validation_html/database.html
"""
from __future__ import annotations
import csv
import io
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "Models" / "CALIBRATION_AND_VALIDATION" / "curve_library"
FOLDERS = [
    ("digitized_csv", "Curvas F/F0 de FIGURAS (alta fidelidade)", "preload"),
    ("extracted_csv", "Curvas F/F0 de TABELAS (aproximadas)", "preload"),
    ("theta_csv", "Rotacao da porca θ(N) — extração vetorial de PDF", "theta"),
    ("loops_csv", "Loops de histerese F×δ", "loop"),
    ("anchors_csv", "Tabelas-âncora medidas (razões, limiares, escalares)", "anchor"),
]
CSS = """body{margin:0;background:#e8eaed;color:#1a1e24;font-family:'Segoe UI',sans-serif;line-height:1.5}
.wrap{max-width:1050px;margin:0 auto;padding:24px 20px 60px}
h1{font-size:20px;margin:4px 0} h2{font-size:14px;margin:22px 0 6px;color:#2f6690}
table{border-collapse:collapse;width:100%;font-size:12px;background:#f8f9fa;border:1px solid #c9ced5}
td,th{padding:4px 8px;border-bottom:1px solid #dfe3e7;text-align:left;font-variant-numeric:tabular-nums}
th{font-family:Consolas,monospace;font-size:10.5px;text-transform:uppercase;color:#5c6570}
code{font-family:Consolas,monospace;font-size:11px;color:#2f6690}
.sub{font-family:Consolas,monospace;font-size:11px;color:#5c6570}"""


def scan(folder: Path):
    rows = []
    for f in sorted(folder.glob("*.csv")):
        try:
            with io.open(f, encoding="utf-8") as fh:
                lines = [ln for ln in fh if ln.strip()]
            src = next((ln.strip("# \n") for ln in lines if ln.startswith("#")), "")
            data = [ln for ln in lines if not ln.startswith("#")]
            hdr = data[0].strip() if data else ""
            n = max(len(data) - 1, 0)
            first = data[1].split(",")[0] if n else ""
            last = data[-1].split(",")[0] if n else ""
            rows.append((f.name, hdr, n, first, last, src))
        except Exception as e:  # arquivo quebrado: reporta, nao explode
            rows.append((f.name, f"ERRO: {e}", 0, "", "", ""))
    return rows


def coverage():
    """status de USO por arquivo: galeria (validado vs modelo), confrontado
    (theta/loops secs 4.23/4.25), usado em harness, ou NAO usado."""
    import json, glob
    rd = json.load(io.open(ROOT / "New_Theory" / "report_data.json", encoding="utf-8"))
    gal = {c["csv"] for c in rd["gallery"]}
    htxt = ""
    for f in glob.glob(str(ROOT / "New_Theory" / "*.py")):
        htxt += io.open(f, encoding="utf-8", errors="ignore").read()
    out = {}
    for folder, _, _ in FOLDERS:
        d = LIB / folder
        if not d.exists():
            continue
        sts = {}
        unused_src = {}
        for f in sorted(d.glob("*.csv")):
            if folder == "theta_csv":
                st = "confrontado"
            elif folder == "loops_csv":
                st = "confrontado"
            elif f.stem in gal:
                st = "galeria"
            elif f.stem in htxt:
                st = "harness"
            else:
                st = "nao usado"
                src = f.stem.split("_")[0]
                unused_src[src] = unused_src.get(src, 0) + 1
            sts[st] = sts.get(st, 0) + 1
        out[folder] = (sts, unused_src)
    return out


def main():
    parts, kpis = [], []
    total = 0
    for name, desc, _kind in FOLDERS:
        folder = LIB / name
        if not folder.exists():
            parts.append(f"<h2>{name} — {desc}</h2><p class='sub'>(pasta ainda nao existe)</p>")
            continue
        rows = scan(folder)
        total += len(rows)
        kpis.append(f"{name}: {len(rows)}")
        by_src = defaultdict(int)
        for r in rows:
            by_src[r[0].split("_")[0]] += 1
        trs = "".join(
            f"<tr><td><code>{fn}</code></td><td class='sub'>{hdr[:60]}</td>"
            f"<td>{n}</td><td class='sub'>{a}→{b}</td><td class='sub'>{src[:90]}</td></tr>"
            for fn, hdr, n, a, b, src in rows)
        parts.append(
            f"<h2>{name} ({len(rows)}) — {desc}</h2>"
            f"<p class='sub'>fontes: {', '.join(f'{k} ({v})' for k, v in sorted(by_src.items()))}</p>"
            f"<table><tr><th>arquivo</th><th>colunas</th><th>pts</th><th>span</th>"
            f"<th>proveniência (linha #)</th></tr>{trs}</table>")
    cov = coverage()
    cov_rows = ""
    for folder, (sts, unused) in cov.items():
        tot = sum(sts.values())
        top = ", ".join(f"{k}({v})" for k, v in sorted(unused.items(), key=lambda kv: -kv[1])[:8])
        cov_rows += (f"<tr><td><code>{folder}</code></td><td>{tot}</td>"
                     f"<td>{sts.get('galeria', 0)}</td><td>{sts.get('confrontado', 0)}</td>"
                     f"<td>{sts.get('harness', 0)}</td><td><b>{sts.get('nao usado', 0)}</b></td>"
                     f"<td class='sub'>{top}</td></tr>")
    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>BAS V2 — database de curvas</title><style>{CSS}</style></head><body><div class="wrap">
<p class="sub"><a href="index.html">&larr; index</a> · <a href="variables.html">variáveis</a> · <a href="dashboard.html">painel</a></p>
<h1>Database de curvas da literatura — {total} arquivos</h1>
<p class="sub">catálogo gerado por New_Theory/generate_database_html.py (varredura dinâmica das pastas);
diretiva 2026-07-08: tudo por literatura — curvas de preload + θ(N) + loops + tabelas-âncora</p>
<h2>Cobertura de VALIDAÇÃO (quanto do database já confrontou o modelo)</h2>
<table><tr><th>pasta</th><th>total</th><th>galeria</th><th>confrontado</th><th>harness</th><th>NÃO usado</th><th>não-usados por fonte (top)</th></tr>
{cov_rows}</table>
<p class="sub">galeria = curva validada no painel · confrontado = θ (§4.23) / loops (§4.25) ·
harness = usado em análise · NÃO usado = fila da campanha de cobertura (âncoras → proveniência
por constante; curvas → classes novas de física: reaperto, CFRP, térmico, torsional, multi-parafuso)</p>
{''.join(parts)}
</div></body></html>"""
    out = ROOT / "New_Theory" / "validation_html" / "database.html"
    out.write_text(html, encoding="utf-8")
    print(f"wrote {out} ({total} csvs)")


if __name__ == "__main__":
    main()
