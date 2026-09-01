"""INDICADOR DE CONVERGÊNCIA da campanha /converge-model (2026-07-08).

Calcula o erro global (média E mediana de MAE) sobre TODOS os casos da galeria
(New_Theory/report_data.json — 62: 46 transversal + 13 axial + 3 HDPE), compara
com os PISOS medidos por fonte (limite físico: repetibilidade do próprio dado),
apende uma entrada ao ledger persistente e responde CONVERGIU?/continua.

Critério de convergência (mínimo global operacional):
  (a) todo caso ≤ max(piso_da_fonte + 0.02, TARGET) — está no limite do dado; OU
  (b) Δ(média global) < EPS por PATIENCE entradas consecutivas do ledger.

Run: python New_Theory/convergence_indicator.py [--note "texto"]
"""
from __future__ import annotations
import json
import sys
import datetime
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "New_Theory" / "report_data.json"
LEDGER = ROOT / "New_Theory" / "convergence_ledger.json"

TARGET = 0.10          # "erro baixo" alvo por caso quando nao ha piso medido
EPS = 0.002            # melhoria minima da media global por iteracao
PATIENCE = 3           # iteracoes sem melhoria > EPS => convergiu (minimo global)

# pisos de repetibilidade MEDIDOS (MAE pareado entre repeats do proprio dado)
# ("LU_2024","fig20") REMOVIDO 2026-07-31: fig20 nao tem replicas (5 torques
# na mesma amplitude) — o 0.093 media cruzamento de condicao; ver
# lu2024_plano_melhoria.md A2 e o espelho em report_html.FLOORS.
FLOORS = {("BAUER_2024", "fig6"): 0.115, ("BAUER_2024", "fig8"): 0.093,
          ("KARLSEN_2022", ""): 0.115,
          ("YANG_2019", ""): 0.081}


def floor_of(g):
    for (src, tok), f in FLOORS.items():
        if g["source"] == src and (tok == "" or tok in g["csv"]):
            return f
    return 0.0


def write_dashboard(gal, ledger, above):
    """Painel ao vivo (auto-refresh 15s): erro por curva, limites, tendencia global."""
    out = ROOT / "New_Theory" / "validation_html" / "dashboard.html"
    e = ledger[-1]
    above_set = {c for c, _, _ in above}
    xs = list(range(len(ledger)))
    ms = [x["mean"] for x in ledger]
    mmax = max(ms) * 1.05 if ms else 1
    pts = " ".join(f"{20+i*(560/max(len(xs)-1,1)):.0f},{80-70*m/mmax:.1f}"
                   for i, m in enumerate(ms))
    trend = (f'<svg viewBox="0 0 600 95" style="width:100%;max-width:640px">'
             f'<polyline points="{pts}" fill="none" stroke="#2f6690" stroke-width="2"/>'
             f'<text x="20" y="92" font-size="10" fill="#8b939c" font-family="Consolas">'
             f'iter 0..{len(ledger)-1} — media global {e["mean"]:.4f}</text></svg>')
    by = {}
    for g in gal:
        by.setdefault(g["source"], []).append(g)
    rows = []
    for src in sorted(by):
        rows.append(f'<tr><td colspan="3" style="padding-top:10px"><b>{src}</b></td></tr>')
        for g in sorted(by[src], key=lambda x: -x["mae"]):
            bound = max(floor_of(g) + 0.02, TARGET)
            pct = min(g["mae"] / 0.30, 1.0) * 100
            color = ("#c0392b" if g["csv"] in above_set else
                     "#e0a24e" if g["mae"] > bound * 0.8 else "#3f8f5f")
            rows.append(
                f'<tr><td style="font-family:Consolas;font-size:11px">{g["csv"]}</td>'
                f'<td style="width:45%"><div style="background:#eef0f2;border-radius:4px">'
                f'<div style="width:{pct:.0f}%;background:{color};height:10px;'
                f'border-radius:4px"></div></div></td>'
                f'<td style="font-family:Consolas;font-size:11px;text-align:right">'
                f'{g["mae"]:.3f} <span style="color:#8b939c">/ {bound:.2f}</span></td></tr>')
    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<meta http-equiv="refresh" content="15">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>BAS V2 — convergencia ao vivo</title>
<style>body{{margin:0;background:#e8eaed;color:#1a1e24;font-family:'Segoe UI',sans-serif}}
.wrap{{max-width:900px;margin:0 auto;padding:20px}}
.card{{background:#f8f9fa;border:1px solid #c9ced5;border-radius:8px;padding:14px 16px;margin-bottom:14px}}
table{{border-collapse:collapse;width:100%}} td{{padding:3px 6px}}
h1{{font-size:18px;margin:0 0 4px}}</style></head><body><div class="wrap">
<h1>Convergencia — erro por curva (ao vivo, refresh 15 s)</h1>
<p style="font-family:Consolas;font-size:12px;color:#5c6570">{e['ts']} · iter {len(ledger)-1} ·
MEDIA {e['mean']:.4f} · mediana {e['median']:.4f} · acima do limite: {e['n_above_bound']}/{e['n']}
· nota: {e.get('note','')}</p>
<div class="card">{trend}</div>
<div class="card"><table>{''.join(rows)}</table>
<p style="font-family:Consolas;font-size:10px;color:#8b939c">barra = MAE (escala ate 0.30) ·
verde = no limite do dado · ambar = perto · vermelho = acima (fila de trabalho) ·
valor / limite (piso medido + 0.02, ou 0.10)</p></div>
</div></body></html>"""
    out.write_text(html, encoding="utf-8")


def main():
    note = ""
    if "--note" in sys.argv:
        note = sys.argv[sys.argv.index("--note") + 1]
    gal = json.loads(DATA.read_text(encoding="utf-8"))["gallery"]
    maes = np.array([g["mae"] for g in gal])
    by = {}
    for g in gal:
        by.setdefault(g["source"], []).append(g["mae"])
    above = [(g["csv"], g["mae"], max(floor_of(g) + 0.02, TARGET))
             for g in gal if g["mae"] > max(floor_of(g) + 0.02, TARGET)]
    above.sort(key=lambda x: -(x[1] - x[2]))

    entry = dict(ts=datetime.datetime.now().isoformat(timespec="seconds"),
                 n=len(gal), mean=float(np.mean(maes)), median=float(np.median(maes)),
                 max=float(np.max(maes)), n_above_bound=len(above),
                 per_source={s: round(float(np.median(m)), 4) for s, m in sorted(by.items())},
                 note=note)
    ledger = json.loads(LEDGER.read_text(encoding="utf-8")) if LEDGER.exists() else []
    prev = ledger[-1] if ledger else None
    ledger.append(entry)
    LEDGER.write_text(json.dumps(ledger, indent=1), encoding="utf-8")

    print(f"== INDICADOR ({entry['ts']}) ==")
    print(f"  casos={entry['n']}  MEDIA={entry['mean']:.4f}  mediana={entry['median']:.4f}  "
          f"max={entry['max']:.3f}")
    if prev:
        print(f"  Δmedia vs anterior: {entry['mean'] - prev['mean']:+.4f}")
    print(f"  acima do limite (piso+0.02 ou {TARGET}): {len(above)}")
    for csv, m, b in above[:10]:
        print(f"    {csv:44s} {m:.3f} (limite {b:.3f})")

    write_dashboard(gal, ledger, above)

    conv_a = len(above) == 0
    recent = [e["mean"] for e in ledger[-(PATIENCE + 1):]]
    conv_b = (len(recent) == PATIENCE + 1
              and all(recent[i] - recent[i + 1] < EPS for i in range(PATIENCE)))
    if conv_a:
        print("\nCONVERGIU (a): todos os casos no limite do dado (pisos) ou <= alvo.")
    elif conv_b:
        print(f"\nCONVERGIU (b): Δmedia < {EPS} por {PATIENCE} iteracoes — minimo global operacional.")
    else:
        print("\nNAO convergiu — continuar a campanha (piores casos acima).")
    sys.exit(0 if (conv_a or conv_b) else 3)


if __name__ == "__main__":
    main()
