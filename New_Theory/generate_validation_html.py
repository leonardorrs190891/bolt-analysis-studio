"""Gera um HTML standalone POR CASO de validacao (62: 49 transversal + 13 axial)
+ index.html, a partir do gallery do report_data.json (curvas ja computadas nas
configs de fronteira declaradas — nenhuma re-simulacao).

Cada pagina: condicoes de contorno (com proveniencia), config usada, plot SVG
inline (dado vs modelo), metricas. Saida: New_Theory/validation_html/.

Run: python New_Theory/generate_validation_html.py <path_do_report_data.json>
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "New_Theory"))
import transfer_validation as tv  # noqa: E402

OUTDIR = ROOT / "New_Theory" / "validation_html"

GROUP = {
    "LIU_2025": ("Liu 2025 — M16 amplitude sweep", "transverse",
                 "slip-regime pack (c_bend=0.3)"),
    "YANG_2019": ("Yang 2019 — M10", "transverse", "slip-regime pack"),
    "ROUSSEAU_2025": ("Rousseau 2025 — M12 thickness", "transverse",
                      "pack + fine-ground embedding (§4.12)"),
    "KARLSEN_2022": ("Karlsen 2022 — M30/M42 HV", "transverse",
                     "c_bend=2.5 (gate opened; §4.15)"),
    "LU_2024": ("Lu 2024 — M8 sweeps", "transverse",
                "kinematic ratchet k=0.02 + c_bend=0.7 (§4.15)"),
    "ICMEZ_2025": ("Içmez 2025 — M12 grip/force", "transverse",
                   "arrest floor 0.25 read from plateau (§4.15)"),
    "BAUER_2024": ("Bauer 2024 — M8 repeats + M12", "transverse",
                   "baseline (model at the data's repeat-scatter floor 0.115)"),
    "ROUSSEAU_HDPE": ("Rousseau 2025 — HDPE members", "transverse",
                      "polymer constants k_j=2e7, k_creep=3 (§4.12 form-transfer)"),
    "LIU_2017_P0": ("Liu 2017 — axial preload sweep", "axial",
                    "per-rig ground-fit block (§4.14a-rev): emb 4.3µm, N_emb 15, "
                    "C_creep 1.45e-11, exp_fast 2.4, exp_slow 3.6, p_ref=p(15kN)"),
    "LIU_2017_AF": ("Liu 2017 — axial amplitude sweep", "axial",
                    "ground-fit block (A_F-blind — the §4.6 amplitude gap is shown, not hidden)"),
    "LI_2022TI": ("Li 2022 — axial × frequency (Ti)", "axial",
                  "zero-refit: frozen Stage-A constants + Rz<10 handbook embedding"),
    "ZHANG_2006": ("Zhang 2006 — M12 grip/direção", "transverse",
                   "per-rig floor 0.10 + N_emb 8 (dado tabela-aproximado, §4.22/§4.34)"),
    "LIU_2022": ("Liu 2022 — fig5 transversal", "transverse",
                 "zero-refit predição (fonte NOVA gerada, §4.28)"),
    "LIU_2022_RET": ("Liu 2022 — reaperto (fig9/fig10)", "transverse",
                     "retighten() + emb renewal + galling per-lube (§4.10/§4.11)"),
}

# pisos de repetibilidade medidos (MAE pareado entre repeats do proprio dado)
FLOORS = {"BAUER_2024": (0.115, "6 repeats fig6"),
          "KARLSEN_2022": (0.115, "4 repeats @1.0mm"),
          "YANG_2019": (0.081, "2 quasi-repeats amp0.6")}

AXIAL_BC = {
    "LIU_2017_P0": dict(bolt="M12×1.75 gr. 10.9 (ground)", grip="30 mm (2.5d, assumed)",
                        freq="30 Hz", mu="0.15 (assumed)", rz="Rz<4 (handbook, Bolt Science)"),
    "LIU_2017_AF": dict(bolt="M12×1.75 gr. 10.9 (ground)", grip="30 mm (2.5d, assumed)",
                        freq="30 Hz", mu="0.15 (assumed)", rz="Rz<4 (handbook)",
                        F0="18 kN"),
    "LI_2022TI": dict(bolt="M10×1.5 (Ti)", grip="25 mm (2.5d, assumed)",
                      mu="0.15 (assumed)", rz="Rz<10 (assumed)", F0="10 kN",
                      F_amp="10 kN"),
}

CSS = """
body{margin:0;background:#e8eaed;color:#1a1e24;font-family:'Segoe UI',system-ui,sans-serif;line-height:1.55}
.wrap{max-width:860px;margin:0 auto;padding:28px 20px 60px}
h1{font-size:22px;margin:6px 0 2px;letter-spacing:-0.01em}
.sub{font-family:Consolas,monospace;font-size:12px;color:#5c6570;margin:0 0 18px}
.grid{display:grid;grid-template-columns:280px 1fr;gap:16px}
@media(max-width:720px){.grid{grid-template-columns:1fr}}
.card{background:#f8f9fa;border:1px solid #c9ced5;border-radius:8px;padding:14px 16px}
h2{font-size:12px;font-family:Consolas,monospace;text-transform:uppercase;letter-spacing:0.08em;color:#5c6570;margin:0 0 8px}
table{border-collapse:collapse;width:100%;font-family:Consolas,monospace;font-size:12.5px}
td{padding:5px 4px;border-bottom:1px solid #dfe3e7;vertical-align:top}
td:first-child{color:#5c6570;white-space:nowrap;padding-right:12px}
tr:last-child td{border-bottom:none}
.metric{font-size:26px;font-weight:700;color:#2f6690;font-family:Consolas,monospace}
.cfg{font-size:12px;color:#454b54;background:#eef0f2;border-radius:6px;padding:8px 10px;margin-top:8px}
svg{display:block;width:100%;height:auto;background:#f8f9fa;border:1px solid #c9ced5;border-radius:8px}
a{color:#2f6690}
.foot{font-family:Consolas,monospace;font-size:11px;color:#8b939c;margin-top:22px;border-top:1px solid #c9ced5;padding-top:10px}
.idx td a{text-decoration:none}
.hub{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:12px;margin:0 0 22px}
.hub .card{padding:12px 14px}
.hub a.t{font-weight:700;text-decoration:none;font-size:14px}
.hub .d{font-size:12px;color:#454b54;margin:4px 0 6px;line-height:1.45}
.hub .m{font-family:Consolas,monospace;font-size:11.5px;color:#2f6690;font-weight:700}
.hgroup{font-size:12px;font-family:Consolas,monospace;text-transform:uppercase;letter-spacing:0.08em;color:#5c6570;margin:18px 0 8px}
"""


def svg_plot(g):
    import math
    W, H, ml, mr, mt, mb = 760, 360, 52, 16, 14, 34
    iw, ih = W - ml - mr, H - mt - mb
    axial = g.get("family") == "axial"
    xmax = max(g["n_max"], max(g["data"]["x"] + [1]))
    xmin = 1 if axial else 0

    def sx(x):
        if axial:
            import math
            la, lb = math.log10(max(xmin, 1)), math.log10(xmax)
            return ml + (math.log10(max(x, xmin)) - la) / max(lb - la, 1e-9) * iw
        return ml + (x - xmin) / max(xmax - xmin, 1e-9) * iw

    def sy(y):
        return mt + (1 - y / 1.05) * ih

    parts = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">']
    for t in (0.0, 0.25, 0.5, 0.75, 1.0):
        y = sy(t)
        parts.append(f'<line x1="{ml}" y1="{y:.1f}" x2="{W-mr}" y2="{y:.1f}" stroke="#dfe3e7"/>')
        parts.append(f'<text x="{ml-6}" y="{y+3:.1f}" text-anchor="end" font-size="10" '
                     f'fill="#8b939c" font-family="Consolas">{t:g}</text>')
    parts.append(f'<line x1="{ml}" y1="{mt}" x2="{ml}" y2="{H-mb}" stroke="#c9ced5"/>')
    parts.append(f'<line x1="{ml}" y1="{H-mb}" x2="{W-mr}" y2="{H-mb}" stroke="#c9ced5"/>')
    xticks = [1, 10, 100, 1e3, 1e4, 1e5, 1e6] if axial else [0, xmax / 2, xmax]
    for xt_ in xticks:
        if xt_ > xmax or (not axial and xt_ < xmin):
            continue
        x = sx(xt_)
        lbl = (f"{int(xt_):,}".replace(",", " ") if xt_ < 1e4
               else f"{xt_:.0e}".replace("e+0", "e"))
        parts.append(f'<text x="{x:.1f}" y="{H-mb+14}" text-anchor="middle" font-size="10" '
                     f'fill="#8b939c" font-family="Consolas">{lbl}</text>')
    pts = " ".join(f"{sx(x):.1f},{sy(min(y,1.05)):.1f}"
                   for x, y in zip(g["model"]["x"], g["model"]["y"]) if x >= xmin or not axial)
    parts.append(f'<polyline points="{pts}" fill="none" stroke="#2f6690" stroke-width="2.4" '
                 f'stroke-linejoin="round"/>')
    for x, y in zip(g["data"]["x"], g["data"]["y"]):
        parts.append(f'<circle cx="{sx(max(x, xmin) if axial else x):.1f}" cy="{sy(min(y,1.05)):.1f}" '
                     f'r="3" fill="#f8f9fa" stroke="#454b54" stroke-width="1.6"/>')
    # rotulos de eixo com unidade (pedido do professor 2026-07-09)
    xunit = ("tempo t [min]" if g.get("family") == "creep"
             else "ciclos N" + (" (log)" if axial else ""))
    parts.append(f'<text x="{ml+iw/2:.0f}" y="{H-2}" text-anchor="middle" font-size="12" '
                 f'fill="#454b54" font-family="Segoe UI">{xunit}</text>')
    parts.append(f'<text x="14" y="{mt+ih/2:.0f}" text-anchor="middle" font-size="12" '
                 f'fill="#454b54" font-family="Segoe UI" '
                 f'transform="rotate(-90 14 {mt+ih/2:.0f})">F / F₀  (razão de pré-carga) [–]</text>')
    parts.append("</svg>")
    return "".join(parts)


def bc_rows(g, tvcases):
    src = g["source"]
    rows = []
    stem = g["csv"]
    case = tvcases.get(stem)
    if case is not None:
        inp = tv.inputs_for(case)
        rows += [("bolt", case.bolt_size), ("F₀", f"{case.initial_preload_N/1e3:.1f} kN"),
                 ("amplitude", f"±{case.transverse_displacement_mm} mm (disp-controlled)"),
                 ("frequency", f"{case.frequency_Hz:g} Hz"),
                 ("grip", f"{inp['grip_mm']['value']:g} mm ({inp['grip_mm']['prov']})"),
                 ("μ", f"{inp['mu']['value']:g} ({inp['mu']['prov']})"),
                 ("surface", f"{inp['rz']['value']} ({inp['rz']['prov']})"),
                 ("F_amp", f"{inp['F_amp_N']['value']/1e3:.1f} kN (0.4·F₀ — lit.: Pai&Hess 2002 mediu 0.38–0.49)")]
    elif src in AXIAL_BC:
        d = dict(AXIAL_BC[src])
        if src == "LIU_2017_P0":
            d["F0"] = stem.split("F0_")[1].replace("p", ".").replace("kN", " kN")
            d["F_amp"] = "10 kN (axial, force-controlled)"
        if src == "LIU_2017_AF":
            d["F_amp"] = stem.split("AF_")[1].replace("p", ".").replace("kN", " kN (axial)")
        if src == "LI_2022TI":
            d["freq"] = stem.split("_")[-1].replace("Hz", " Hz") if "Hz" in stem else "10 Hz"
        rows += list(d.items())
    elif src == "ROUSSEAU_HDPE":
        grip = {"t10": 25, "t12": 29, "t14": 33}[stem[-3:]]
        rows += [("bolt", "M12×1.75 gr. 8.8"), ("members", f"HDPE, grip {grip} mm"),
                 ("F₀", "~10.3 kN"), ("amplitude", "±0.5 mm (disp)"), ("frequency", "1 Hz"),
                 ("k_j (polymer)", "2e7 N/m"), ("μ", "0.15 (assumed)")]
    rows.append(("cycles", f"{g['n_max']:,}".replace(",", " ")))
    return rows


def _nfail(x, y, thr=0.5):
    for i, v in enumerate(y):
        if v <= thr:
            if i == 0:
                return x[0] or 1
            t = (thr - y[i]) / ((y[i - 1] - y[i]) or 1e-9)
            return x[i] + t * (x[i - 1] - x[i])
    return None


def page(g, tvcases, nav):
    name, family, cfg = GROUP[g["source"]]
    bc = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in bc_rows(g, tvcases))
    fin_d = g["data"]["y"][-1]
    fin_m = g["model"]["y"][-1]
    nd = _nfail(g["data"]["x"], g["data"]["y"])
    nm = _nfail(g["model"]["x"], g["model"]["y"])
    life = (f"<tr><td>N to F/F₀=0.5 (data)</td><td>{nd:.0f}</td></tr>"
            f"<tr><td>N to F/F₀=0.5 (model)</td><td>{nm:.0f}</td></tr>"
            f"<tr><td><b>life ratio (model/data)</b></td><td><b>{nm/nd:.2f}×</b> "
            f"(factor-2 band is the fatigue-engineering norm)</td></tr>"
            if (nd and nm) else "")
    fl = FLOORS.get(g["source"])
    floor = (f"<tr><td>repeat-scatter floor</td><td>{fl[0]:.3f} ({fl[1]}) — the data's "
             f"own repeats disagree by this much; MAE at/below it is unimprovable</td></tr>"
             if fl else "")
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{g['csv']} — BAS V2 validation</title><style>{CSS}</style></head><body>
<div class="wrap">
<p class="sub"><a href="index.html">← index</a> · {name} · {family}</p>
<h1>{g['csv']}</h1>
<p class="sub">Bolt Analysis Studio V2 — DynamicStiffnessAnalyzer · validation case</p>
{svg_plot(g)}
<div class="grid" style="margin-top:16px">
<div class="card"><h2>Boundary conditions</h2><table>{bc}</table>
<div class="cfg"><b>Configuration:</b> {cfg}</div></div>
<div class="card"><h2>Result</h2>
<div class="metric">MAE {g['mae']:.4f}</div>
<table style="margin-top:8px">
<tr><td>final F/F₀ (data)</td><td>{fin_d:.3f}</td></tr>
<tr><td>final F/F₀ (model)</td><td>{fin_m:.3f}</td></tr>
<tr><td>final error</td><td>{fin_m-fin_d:+.3f}</td></tr>
{life}{floor}
<tr><td>family</td><td>{family}</td></tr></table>
<div class="cfg">Dots = digitized paper data; line = model at the declared per-rig
configuration. Verdicts and falsification records: <code>New_Theory/MODEL_LEGITIMACY.md</code>
§4.12–§4.15.</div></div></div>
<p class="foot">{nav} · generated 2026-07-08 · configs and constants carry declared provenance
(paper / handbook / assumed / read-from-data / fitted-this-rig)</p>
</div></body></html>"""


def main():
    data_path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "New_Theory" / "report_data.json"
    d = json.loads(data_path.read_text(encoding="utf-8"))
    gallery = d["gallery"]
    OUTDIR.mkdir(exist_ok=True)
    cases, _ = tv.select_cases()
    tvcases = {Path(c.reference_csv_path).stem: c for c in cases}

    by_src = {}
    for g in gallery:
        by_src.setdefault(g["source"], []).append(g)
    order = [s for s in GROUP if s in by_src]

    for src in order:
        gs = by_src[src]
        for i, g in enumerate(gs):
            prev = gs[i - 1]["csv"] + ".html" if i > 0 else None
            nxt = gs[i + 1]["csv"] + ".html" if i < len(gs) - 1 else None
            nav = " · ".join(x for x in [
                f'<a href="{prev}">← prev</a>' if prev else "",
                f'<a href="{nxt}">next →</a>' if nxt else ""] if x)
            (OUTDIR / f"{g['csv']}.html").write_text(page(g, tvcases, nav), encoding="utf-8")

    # hub de estudos/galerias (numeros lidos ao vivo dos JSONs; degrada se ausentes)
    def _mean_maes(path, keys):
        try:
            rs = json.loads((ROOT / "New_Theory" / path).read_text(encoding="utf-8"))
            import statistics
            return {k: statistics.mean(e[k]["mae"] for e in rs) for k in keys}, len(rs)
        except Exception:
            return None, 0

    ax_m, ax_n = _mean_maes("axial_emb_provenance_cap1000000.json",
                            ("handbook", "data_implied"))
    if ax_m is None:
        ax_m, ax_n = _mean_maes("axial_emb_provenance.json",
                                ("handbook", "data_implied"))
    tr_m, tr_n = _mean_maes("transverse_provenance.json", ("naive", "adopted"))
    ax_metric = (f"{ax_n} cond. · MAE {ax_m['handbook']:.3f} → {ax_m['data_implied']:.3f}"
                 if ax_m else "12 condições")
    tr_metric = (f"{tr_n} curvas · MAE {tr_m['naive']:.3f} → {tr_m['adopted']:.3f}"
                 if tr_m else "46 curvas")

    def hub_card(href, title, desc, metric=""):
        if not (OUTDIR / href).exists():
            return ""
        m = f'<div class="m">{metric}</div>' if metric else ""
        return (f'<div class="card"><a class="t" href="{href}">{title}</a>'
                f'<div class="d">{desc}</div>{m}</div>')

    hub = (
        '<div class="hgroup">Interface única — explorar tudo</div>'
        '<div class="hub">'
        + hub_card("loosening_explorer.html", "Explorador de loosening",
                   "As 82 curvas numa página interativa: dado do artigo × curva do "
                   "software × erro, com filtros por fonte/família, ordenação por "
                   "erro e detalhe com subplot ε(N).",
                   f"{len(gallery)} curvas · dado × modelo × erro")
        + hub_card("validation_report.html", "Casos de validação — documento",
                   "Índice mestre dos casos + report individual completo de cada um: "
                   "condições de contorno, modelo MSD (junta), constantes usadas com "
                   "proveniência, e curva com erro.",
                   f"{len(gallery)} reports · BC + MSD + constantes")
        + hub_card("MODEL_MATH_REFERENCE.md", "Referência do modelo",
                   "Documentação completa do engine V2: paradigma, estado lento, os 6 "
                   "mecanismos (equações), modos/regimes/gates, capabilities opt-in, "
                   "energia, calibração e DOF.", "markdown · MODEL_MATH_REFERENCE.md")
        + '</div>'
        '<div class="hgroup">Estudos de proveniência (§4.40–4.41) — dado × modelo com erros</div>'
        '<div class="hub">'
        + hub_card("axial_emb_provenance.html", "Proveniência do emb AXIAL",
                   "12 condições (Liu2017 F0+A_F, Li2022ti freq): emb handbook VDI vs "
                   "data-implícito da queda-inicial + painel das leis físicas "
                   "(emb∝A_F/F₀ R²=0.89, emb∝1/freq).", ax_metric)
        + hub_card("transverse_provenance.html", "Proveniência do nível TRANSVERSAL",
                   "46 curvas, 7 fontes: naive-frozen (c_bend=1) vs adotado per-rig. "
                   "Contraste com o axial: nível fitado, não legível do dado.", tr_metric)
        + hub_card("sensitivity.html", "Sensibilidade + redução de variáveis",
                   "Inventário dos 88 campos classificados (88 ≠ 88 DOF) + tornado "
                   "OAT ±20% por família + propostas de redução (merge K/H, "
                   "congelar insensíveis, Estágio B).",
                   "9 casos · S por parâmetro · §4.42")
        + hub_card("theta_loosening.html", "Gráficos de loosening (θ)",
                   "Rotação da porca dado × modelo, zero-refit: 6 curvas θ(N) "
                   "Rousseau (aço + HDPE, t10/t12/t14) com erros; confronto §4.23 "
                   "(free-spin visível, não escondido).",
                   "6 curvas θ(N) · aço t12 MAE 0.27°")
        + '</div>'
        '<div class="hgroup">Visão geral</div>'
        '<div class="hub">'
        + hub_card("all_graphs.html", "Todas as curvas com erro",
                   "As 82 curvas da galeria (transversal + axial + HDPE + Zhang + "
                   "reaperto), cada uma com banda de erro |modelo−dado|.")
        + hub_card("dashboard.html", "Convergência",
                   "Indicador de convergência da campanha (MAE global por rodada).")
        + hub_card("database.html", "Database de curvas",
                   "Base de curvas da biblioteca (CSVs extraídos + digitalizados).")
        + hub_card("variables.html", "Variáveis do modelo",
                   "Inventário de variáveis, análise dimensional (grupos Π) e "
                   "classes de não-linearidade.")
        + '</div>'
        '<div class="hgroup">Relatórios por fonte</div>'
        '<div class="hub">'
        + hub_card("bauer_report.html", "BAUER_2024",
                   "fig6 quase-linear + fig8 espectro: continuum s_crit, colapso mostrado.")
        + hub_card("lu_report.html", "LU_2024",
                   "Refit fig18/fig20 (§4.19/§4.29): amplitude sweep + torque sweep.")
        + hub_card("liu2022_msd.html", "LIU_2022 fig5",
                   "Curvas, predição zero-refit e modelo MSD do rig de reaperto.")
        + '</div>')

    # index
    rows = []
    for src in order:
        name, family, cfg = GROUP[src]
        gs = by_src[src]
        med = sorted(x["mae"] for x in gs)[len(gs) // 2]
        rows.append(f'<tr><td colspan="3" style="padding-top:14px"><b>{name}</b> '
                    f'<span style="color:#8b939c">({family} · {len(gs)} cases · median MAE '
                    f'{med:.3f} · {cfg})</span></td></tr>')
        for g in gs:
            rows.append(f'<tr class="idx"><td><a href="{g["csv"]}.html">{g["csv"]}</a></td>'
                        f'<td>MAE {g["mae"]:.4f}</td><td>final {g["data"]["y"][-1]:.3f} → '
                        f'model {g["model"]["y"][-1]:.3f}</td></tr>')
    idx = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>BAS V2 — índice de validação</title><style>{CSS}</style></head><body>
<div class="wrap"><h1>BAS V2 — índice de validação</h1>
<p class="sub">{len(gallery)} casos ({sum(1 for g in gallery if g.get('family') != 'axial')} transversal
+ {sum(1 for g in gallery if g.get('family') == 'axial')} axial) · galerias de proveniência ·
relatórios por fonte · uma página standalone por caso</p>
{hub}
<div class="hgroup">Caso a caso — cada fonte na sua configuração per-rig declarada</div>
<div class="card"><table>{''.join(rows)}</table></div>
<p class="foot">gerado por New_Theory/generate_validation_html.py ·
casos: src/bolt_analysis_studio/core/validation_cases.py ←
Models/CALIBRATION_AND_VALIDATION/curve_library/ · vereditos: New_Theory/MODEL_LEGITIMACY.md</p></div></body></html>"""
    (OUTDIR / "index.html").write_text(idx, encoding="utf-8")
    print(f"wrote {len(gallery)} case pages + index.html -> {OUTDIR}")


if __name__ == "__main__":
    main()
