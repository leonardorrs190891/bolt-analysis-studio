# -*- coding: utf-8 -*-
"""REPORTS INDIVIDUAIS COMPLETOS dos casos de validacao + indice mestre
(pedido do professor 2026-07-09: "todos os casos de validacao documentados,
incluindo condicoes de contorno, o modelo MSD, e as constantes usadas... reports
completos individuais disponiveis na documentacao do software").

Fontes canonicas (L1 — nunca reconstruir de label):
- New_Theory/report_data.json        — curvas dado/modelo + MAE (harness da galeria)
- core.validation_cases.DIGITIZED_CASES — condicoes de contorno estruturadas
- transfer_validation.inputs_for + library_common.geometry_for — MSD + PROVENIENCIA
- New_Theory/adopted_configs.json    — constantes per-rig adotadas
- profiles.load_shared_material      — constantes fisicas compartilhadas (Estagio A/B)

Gera:
  validation_html/reports/<csv>.html   — 1 report rico por caso (82)
  validation_html/validation_report.html — indice mestre (tabela por fonte)

Run: python New_Theory/generate_case_reports.py
"""
from __future__ import annotations
import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "New_Theory"))

from bolt_analysis_studio.core.validation_cases import DIGITIZED_CASES  # noqa: E402
from bolt_analysis_studio.calibration.profiles import load_shared_material  # noqa: E402
import transfer_validation as tv  # noqa: E402
from library_common import geometry_for  # noqa: E402

OUT = ROOT / "New_Theory/validation_html"
REP = OUT / "reports"
AXIAL_SRC = {"LIU_2017_P0", "LIU_2017_AF", "LI_2022TI"}

NICE = {
    "LIU_2025": "Liu 2025 — M16 shear (Sci. Rep.)",
    "YANG_2019": "Yang 2019 — M10 variable-amplitude (Shock & Vib.)",
    "ROUSSEAU_2025": "Rousseau 2025 — M12 steel members (Materials)",
    "ROUSSEAU_HDPE": "Rousseau 2025 — M12 HDPE members",
    "KARLSEN_2022": "Karlsen & Lemu 2022 — M30/M42 large bolts",
    "LU_2024": "Lu 2024 — M8 amplitude/torque sweeps (Sensors)",
    "ICMEZ_2025": "Icmez/Demir 2024-25 — M12 grip/force (EJRND)",
    "BAUER_2024": "Bauer 2024 — M8/M12 spectrum (Eng. Fail. Anal.)",
    "ZHANG_2006": "Zhang 2006 — M12 grip/direction",
    "LIU_2022": "Liu 2022 — fig5 transverse (Int. J. Struct.)",
    "LIU_2022_RET": "Liu 2022 — retightening (fig9/10)",
    "LIU_2017_P0": "Liu 2017 — axial preload sweep (Tribol. Int.)",
    "LIU_2017_AF": "Liu 2017 — axial amplitude sweep",
    "LI_2022TI": "Li 2022 — axial x frequency, Ti (Tribol. Int.)",
}

# constantes per-rig adotadas (adopted_configs) por fonte — proveniencia
PROV = {
    "c_bend": "fitado-this-rig (compliance transversal, §4.35)",
    "loose_arrest_floor": "lido-do-dado (piso do platô final)",
    "k_ratchet": "fitado-this-rig (ratchet cinemático, §4.15)",
    "delta_free": "lido-do-dado (take-up, regressão de onset §4.19)",
    "k_wear_scale_tr": "fitado-this-rig (LEGADO → k_wear_spec, §4.42)",
    "emb_um": "handbook VDI (Rz) ou data-implícito da queda-inicial (L24, §4.40)",
    "dmg_gross_exp": "compartilhado (onset contínuo de dano, §4.33)",
    "slip_onset_W": "lido-do-dado (incubação, ciclo do platô)",
    "W_crit": "lido-do-dado (energia no joelho medido)",
}
SHARED_PROV = {
    "k_wear_spec": "Estágio A compartilhada — razão K/H [1/Pa] (merge §4.42a)",
    "C_creep": "Estágio A compartilhada — por par tribológico (§4.7)",
    "tr_loose_gain": "Estágio A compartilhada (âncora pendente §4.42)",
    "N_emb": "Estágio A compartilhada (constante de tempo do assentamento)",
    "W_conf_ref": "Estágio A — conformação, por par da âncora interna (§4.9)",
    "conform_pressure_exp": "fixo n=2 (VDI)",
    "p_ref_conform": "computado do %yield (pct/70, roadmap 11f)",
}


def _fnum(v, unit=""):
    if v is None:
        return "—"
    if isinstance(v, float):
        if v == 0:
            return "0" + (" " + unit if unit else "")
        a = abs(v)
        s = f"{v:.4g}" if (a >= 1e-3 and a < 1e5) else f"{v:.3e}"
    else:
        s = str(v)
    return s + (" " + unit if unit else "")


# ---------------------------------------------------------------- SVG plot
def _svg(entry, W=560, H=300):
    ML, MR, MT, MB = 56, 16, 14, 40
    axial = entry["fam"] == "axial"
    dx, dy = entry["data"]["x"], entry["data"]["y"]
    mx, my = entry["model"]["x"], entry["model"]["y"]
    xmax = max(entry["n_max"], dx[-1], 1)
    xmin = 1 if axial else 0

    def lx(x):
        if axial:
            v = math.log10(max(x, 1)); lo = math.log10(max(xmin, 1))
            hi = math.log10(max(xmax, 10))
            return ML + (v - lo) / (hi - lo or 1) * (W - ML - MR)
        return ML + (x - xmin) / (xmax - xmin or 1) * (W - ML - MR)

    def ly(y):
        return MT + (1 - max(y, 0) / 1.08) * (H - MT - MB)

    s = [f'<svg viewBox="0 0 {W} {H}" class="plot" xmlns="http://www.w3.org/2000/svg">']
    for yv in (0, .25, .5, .75, 1):
        yy = ly(yv)
        s.append(f'<line class="gl" x1="{ML}" y1="{yy:.0f}" x2="{W-MR}" y2="{yy:.0f}"/>')
        s.append(f'<text class="tk" x="{ML-6}" y="{yy+3:.0f}" text-anchor="end">{yv:.2f}</text>')
    # interp modelo nos pontos do dado -> barras de erro
    import numpy as np
    mi = np.interp(dx, mx, my)
    for x, a, b in zip(dx, dy, mi):
        s.append(f'<line class="err" x1="{lx(x):.1f}" y1="{ly(a):.1f}" x2="{lx(x):.1f}" y2="{ly(b):.1f}"/>')
    s.append('<polyline class="ml" fill="none" points="'
             + " ".join(f"{lx(x):.1f},{ly(y):.1f}" for x, y in zip(mx, my)) + '"/>')
    for x, y in zip(dx, dy):
        s.append(f'<circle class="pt" cx="{lx(x):.1f}" cy="{ly(y):.1f}" r="2.6"/>')
    s.append(f'<text class="axl" x="{(ML+W-MR)/2:.0f}" y="{H-4}" text-anchor="middle">'
             f'ciclos N{" (log)" if axial else ""}</text>')
    s.append(f'<text class="axl" x="13" y="{(MT+H-MB)/2:.0f}" text-anchor="middle" '
             f'transform="rotate(-90 13 {(MT+H-MB)/2:.0f})">F / F&#8320; [&#8211;]</text>')
    s.append('</svg>')
    return "".join(s)


def _row(label, value, prov=""):
    p = f'<span class="pv">{prov}</span>' if prov else ""
    return f'<tr><td class="k">{label}</td><td class="v">{value}</td><td>{p}</td></tr>'


def report(entry, case, adopted):
    src = entry["source"]
    fam = entry["fam"]
    # geometria MSD + inputs com proveniencia (best-effort)
    bc_rows, msd_rows, const_rows = [], [], []
    inp = {}
    geom = None
    if case is not None:
        try:
            inp = tv.inputs_for(case)
        except Exception:
            inp = {}
        try:
            grip = (inp.get("grip_mm", {}) or {}).get("value") or 30.0
            geom = geometry_for(case.bolt_size, grip_mm=grip)
        except Exception:
            geom = None
        F0 = case.initial_preload_N
        bc_rows += [
            _row("Pré-carga inicial F₀", _fnum(F0/1e3, "kN"),
                 f"{_fnum(getattr(case,'preload_percent_yield',None))}% do escoamento"),
            _row("Modo de carga", "axial (força)" if fam == "axial"
                 else "transversal / disp (Junker)"),
            _row("Amplitude transversal", _fnum(case.transverse_displacement_mm, "mm")
                 if case.transverse_displacement_mm else "— (axial)"),
            _row("Amplitude de força F_amp",
                 _fnum((inp.get("F_amp_N", {}) or {}).get("value"), "N"),
                 (inp.get("F_amp_N", {}) or {}).get("prov", "")),
            _row("Frequência", _fnum(case.frequency_Hz, "Hz")),
            _row("Ciclos (ensaio)", _fnum(case.n_cycles)),
            _row("Lubrificação", "sim" if getattr(case, "lubricated", False) else "seco"),
            _row("ΔT", "0 (isotérmico)"),
        ]
        pitch = getattr(case, "pitch_mm", None)
        msd_rows += [
            _row("Parafuso", f"{case.bolt_size}"),
            _row("Diâmetro nominal / passo",
                 f"{_fnum(getattr(case,'bolt_diameter_mm',None),'mm')} / {_fnum(pitch,'mm')}"),
        ]
        if geom is not None:
            msd_rows += [
                _row("Diâmetro de passo d₂", _fnum(geom.d_2*1e3, "mm")),
                _row("Área de tensão A_s", _fnum(geom.A_s*1e6, "mm²")),
                _row("Comprimento efetivo L_eff (grip)", _fnum(geom.L_eff*1e3, "mm"),
                     (inp.get("grip_mm", {}) or {}).get("prov", "")),
                _row("Rigidez do parafuso k_b", _fnum(geom.k_b/1e6, "MN/m"),
                     "E·A_s/L_eff"),
                _row("Raio de apoio r_bearing / área A_contact",
                     f"{_fnum(geom.r_bearing*1e3,'mm')} / {_fnum(geom.A_contact*1e6,'mm²')}",
                     "anel real π(r_b²−r_furo²), §4.9-11g"),
            ]
        msd_rows += [
            _row("Atrito µ (rosca=apoio)", _fnum((inp.get("mu", {}) or {}).get("value")),
                 (inp.get("mu", {}) or {}).get("prov", "")),
            _row("Rugosidade Rz", _fnum((inp.get("rz", {}) or {}).get("value")),
                 (inp.get("rz", {}) or {}).get("prov", "")),
            _row("Cadeia MSD", "GROUND — bolt shank (k_b) — thread contact (hélice λ, "
                 "atrito) — bearing (µ, wear) — member(s) — flange"),
        ]
    else:
        bc_rows.append(_row("Condições de contorno",
                            f"amplitude {entry.get('amp_mm','?')} mm · n_max {entry['n_max']}",
                            "report_data (caso sem ValidationCase estruturado)"))
    # constantes usadas: config per-rig adotada + shared
    cfg = (adopted or {}).get("cfg", {}) if adopted else {}
    def _walk(d, pfx=""):
        for k, v in d.items():
            if isinstance(v, dict):
                _walk(v, pfx)
            elif isinstance(v, (int, float, str, bool)):
                const_rows.append(_row(pfx + k, _fnum(v),
                                       PROV.get(k, "config adotada per-rig")))
    _walk(cfg)
    shared = load_shared_material()
    for k, v in shared.items():
        const_rows.append(_row(k, _fnum(v), SHARED_PROV.get(k, "Estágio A compartilhada")))
    verdict = (adopted or {}).get("verdict", "") if adopted else ""

    doi = getattr(case, "doi", None) if case else None
    url = getattr(case, "url", None) if case else None
    src_link = (f'<a href="https://doi.org/{doi}">{doi}</a>' if doi
                else (f'<a href="{url}">fonte</a>' if url else ""))
    mae = entry["mae"]
    grade = "good" if mae <= 0.1 else "warn"
    html = f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{entry["csv"]} — report de validação</title>{_CSS}</head><body><div class="wrap">
<p class="back"><a href="../validation_report.html">&#8592; casos de validação</a>
 &#183; <a href="../index.html">índice</a></p>
<h1>{entry["csv"]}</h1>
<p class="sub">{NICE.get(src, src)} &#183; {"axial" if fam=="axial" else "transversal"}
 &#183; {src_link}</p>
<div class="grid2">
  <div>
    <h2>1. Condições de contorno</h2><table>{''.join(bc_rows)}</table>
    <h2>2. Modelo MSD (junta)</h2><table>{''.join(msd_rows)}</table>
  </div>
  <div>
    <h2>Resultado</h2>
    <div class="metric {grade}">MAE {mae:.4f}</div>
    <div class="sub2">interp {entry.get("mae_interp", mae):.4f} &#183; erro máx
      {entry.get("maxerr_interp",0):.3f} @ ciclo {int(entry.get("maxerr_at",0))}</div>
    {_svg(entry)}
    <div class="lg"><span class="s ml"></span>modelo &#183; <span class="s pt"></span>dado
      &#183; <span class="s err"></span>erro |modelo&#8722;dado|</div>
  </div>
</div>
<h2>3. Constantes usadas (com proveniência)</h2>
<table class="wide">{''.join(const_rows)}</table>
{f'<h2>Veredicto de adoção</h2><p class="verd">{verdict}</p>' if verdict else ''}
<p class="foot">Gerado por New_Theory/generate_case_reports.py de report_data.json +
validation_cases + adopted_configs + bloco shared. Veredictos de física:
MODEL_LEGITIMACY.md. Referência do modelo: MODEL_MATH_REFERENCE.md.</p>
</div></body></html>'''
    return html


_CSS = """<style>
:root{--bg:#faf9f7;--fg:#1c1a17;--mut:#6b655c;--card:#fff;--bd:#e6e1d8;--di:#2f6f8f;
 --err:#c0392b;--pt:#1c1a17;--good:#1a7a4c;--warn:#b3452c;--accent:#2f6f8f}
@media(prefers-color-scheme:dark){:root{--bg:#16140f;--fg:#ece7de;--mut:#9a938a;--card:#211e18;
 --bd:#332e26;--di:#6bb6d6;--err:#e8776b;--pt:#ece7de;--good:#5fd39a;--warn:#e8936b;--accent:#6bb6d6}}
:root[data-theme=dark]{--bg:#16140f;--fg:#ece7de;--mut:#9a938a;--card:#211e18;--bd:#332e26;
 --di:#6bb6d6;--err:#e8776b;--pt:#ece7de;--good:#5fd39a;--warn:#e8936b;--accent:#6bb6d6}
:root[data-theme=light]{--bg:#faf9f7;--fg:#1c1a17;--mut:#6b655c;--card:#fff;--bd:#e6e1d8;
 --di:#2f6f8f;--err:#c0392b;--pt:#1c1a17;--good:#1a7a4c;--warn:#b3452c;--accent:#2f6f8f}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);
 font:15px/1.55 -apple-system,"Segoe UI",Roboto,sans-serif;padding:24px 20px 60px}
.wrap{max-width:1000px;margin:0 auto}
.back{font-size:.8rem;margin:0 0 8px}.back a{color:var(--accent);text-decoration:none}
h1{font-size:1.4rem;margin:0 0 2px;font-family:Consolas,monospace}
.sub{color:var(--mut);margin:0 0 18px;font-size:.9rem}.sub a{color:var(--accent)}
.sub2{color:var(--mut);font-size:.78rem;margin:2px 0 8px;font-family:Consolas,monospace}
h2{font-size:.95rem;text-transform:uppercase;letter-spacing:.05em;color:var(--accent);
 margin:20px 0 8px;border-bottom:1px solid var(--bd);padding-bottom:4px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:22px}
@media(max-width:760px){.grid2{grid-template-columns:1fr}}
table{border-collapse:collapse;width:100%;font-size:.82rem}
table.wide{font-size:.8rem}
td{padding:4px 8px;border-bottom:1px solid var(--bd);vertical-align:top}
td.k{color:var(--mut);white-space:nowrap;width:42%}td.v{font-family:Consolas,monospace}
.pv{font-size:.72rem;color:var(--mut)}
.metric{font-size:1.7rem;font-weight:750;font-family:Consolas,monospace}
.metric.good{color:var(--good)}.metric.warn{color:var(--warn)}
.plot{width:100%;height:auto;display:block;margin:6px 0}
.gl{stroke:var(--bd);stroke-width:.6}.tk{fill:var(--mut);font-size:9px}.axl{fill:var(--mut);font-size:10px}
.err{stroke:var(--err);stroke-width:2.2;opacity:.5}.ml{stroke:var(--di);stroke-width:2.2}.pt{fill:var(--pt)}
.lg{font-size:.72rem;color:var(--mut);margin-top:2px}
.lg .s{display:inline-block;width:16px;height:8px;vertical-align:middle;margin:0 3px}
.lg .s.ml{background:var(--di)}.lg .s.pt{background:var(--pt);border-radius:50%;width:8px}
.lg .s.err{background:var(--err);opacity:.5}
.verd{font-size:.82rem;color:var(--fg);background:var(--card);border:1px solid var(--bd);
 border-left:3px solid var(--accent);border-radius:8px;padding:10px 14px;max-width:90ch}
.foot{font-size:.72rem;color:var(--mut);margin-top:22px;border-top:1px solid var(--bd);padding-top:10px}
</style>"""


def master_index(rows_by_src, counts, mean_by_src):
    import numpy as np
    body = []
    total = sum(len(v) for v in rows_by_src.values())
    allmae = [e["mae"] for v in rows_by_src.values() for e in v]
    body.append(f'''<p class="sub">{total} casos de validação · {len(rows_by_src)} fontes ·
      MAE médio {np.mean(allmae):.3f} · mediana {np.median(sorted(allmae)):.3f}.
      Cada linha abre o <b>report individual completo</b> (condições de contorno,
      modelo MSD, constantes usadas com proveniência, curva com erro).</p>''')
    for src in sorted(rows_by_src):
        items = rows_by_src[src]
        trs = "".join(
            f'<tr><td><a href="reports/{e["csv"]}.html">{e["csv"]}</a></td>'
            f'<td>{e.get("amp_mm","—")}</td><td>{e["n_max"]:,}</td>'
            f'<td class="{"good" if e["mae"]<=0.1 else "warn"}">{e["mae"]:.3f}</td></tr>'
            for e in sorted(items, key=lambda z: z["csv"]))
        body.append(f'''<h2>{NICE.get(src, src)} <span class="c">({len(items)} casos ·
          MAE médio {mean_by_src[src]:.3f})</span></h2>
          <table class="idx"><thead><tr><th>caso</th><th>amp [mm]</th><th>ciclos</th>
          <th>MAE</th></tr></thead><tbody>{trs}</tbody></table>''')
    html = f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Casos de validação — documento mestre</title>{_CSS}
<style>.idx{{margin:2px 0 6px}}.idx th{{text-align:right;color:var(--mut);font-weight:600;
 padding:4px 8px;border-bottom:1px solid var(--bd);font-size:.75rem}}
.idx th:first-child{{text-align:left}}.idx td{{text-align:right}}.idx td:first-child{{text-align:left}}
.idx td a{{color:var(--accent);text-decoration:none;font-family:Consolas,monospace}}
.idx .good{{color:var(--good);font-weight:600}}.idx .warn{{color:var(--warn);font-weight:600}}
h2 .c{{font-size:.72rem;color:var(--mut);text-transform:none;letter-spacing:0}}</style>
</head><body><div class="wrap">
<p class="back"><a href="index.html">&#8592; índice de validação</a></p>
<h1>Casos de validação — documento mestre</h1>
{''.join(body)}
<p class="foot">Reports individuais em validation_html/reports/. Gerado de report_data.json +
core.validation_cases + adopted_configs + bloco shared canônico.</p>
</div></body></html>'''
    return html


def main():
    import numpy as np
    gallery = json.loads((ROOT / "New_Theory/report_data.json")
                         .read_text(encoding="utf-8"))["gallery"]
    adopted_all = json.loads((ROOT / "New_Theory/adopted_configs.json")
                             .read_text(encoding="utf-8")).get("sources", {})
    by_case = {os.path.basename(getattr(c, "reference_csv_path", "")).replace(".csv", ""): c
               for c in DIGITIZED_CASES if getattr(c, "reference_csv_path", "")}
    # mapa source -> chave de adopted_configs (best match)
    def adopted_for(src):
        for k in adopted_all:
            if src.split("_")[0].upper() in k.upper():
                return adopted_all[k]
        return None
    REP.mkdir(parents=True, exist_ok=True)
    rows_by_src, mean_by_src = {}, {}
    for e in gallery:
        e = dict(e)
        e["fam"] = e.get("family") or ("axial" if e["source"] in AXIAL_SRC else "transverse")
        case = by_case.get(e["csv"])
        (REP / f'{e["csv"]}.html').write_text(
            report(e, case, adopted_for(e["source"])), encoding="utf-8")
        rows_by_src.setdefault(e["source"], []).append(e)
    for src, items in rows_by_src.items():
        mean_by_src[src] = float(np.mean([x["mae"] for x in items]))
    (OUT / "validation_report.html").write_text(
        master_index(rows_by_src, {s: len(v) for s, v in rows_by_src.items()},
                     mean_by_src), encoding="utf-8")
    print(f"escrito: {len(gallery)} reports em {REP}/ + validation_report.html")
    print(f"  casos com boundary-conditions estruturadas: "
          f"{sum(1 for e in gallery if e['csv'] in by_case)}/{len(gallery)}")


if __name__ == "__main__":
    main()
