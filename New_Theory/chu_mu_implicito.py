"""Sonda do mu IMPLICITO no dado do Chu 2026 — o sinal da Fig. 5 nos nossos CSVs.

Fato medido (kernel_f0slip): no Chu o slip e' CONSTANTE (gross-slip profundo).
Entao a perda slip-driven do engine e' taxa ~ mu * F0 * slip ~ mu(n) * r(n).
Invertendo o DADO:  mu_impl(n) ∝ taxa_dado(n) / r_dado(n).

Se a Fig. 5 do paper esta certa (COF SOBE enquanto afrouxa; mais rapido em F0
baixo; plateau quando cessa), entao mu_impl deve SUBIR nas curvas que
desaceleram (test4/7/8) — e a ordenacao 49 kN > 61 > 73 na velocidade de subida.

Saida: razao mu_fim/mu_inicio e slope log-log por curva + ordenacao por F0.
"""
import sys, json, pathlib
import numpy as np
sys.path.insert(0, str(pathlib.Path('src').resolve()))
from bolt_analysis_studio.validation.case_registry import record
from bolt_analysis_studio.validation.inputs import load_full_curve, repo_root
from bolt_analysis_studio.validation import runner

CURVAS = ['chu2026ti_D0p4mm_F0_49kN_test2', 'chu2026ti_D0p5mm_F0_49kN_test3',
          'chu2026ti_D0p7mm_F0_49kN_test4', 'chu2026ti_D0p4mm_F0_61kN_test7',
          'chu2026ti_D0p4mm_F0_73kN_test8', 'chu2026ti_D0p5mm_F0_49kN_Ra1p6um_test9',
          'chu2026ti_D1p0mm_F0_49kN_test5', 'chu2026ti_D1p0mm_F0_49kN_test6_repeat']
P = print
P('=' * 78)
P('MU IMPLICITO no dado (taxa/r), janela pos-assentamento (>20%% N)')
P('=' * 78)
P('%-42s %8s %10s %12s' % ('curva', 'F0(kN)', 'slope mu', 'mu_fim/ini'))
out = {}
for cid in CURVAS:
    rec = record(cid)
    case = rec.validation_case
    cx, cr = load_full_curve(rec.csv_path.relative_to(repo_root()).as_posix())
    off = float(getattr(case, 'csv_x_offset', 0.0) or 0.0)
    cx = np.maximum(cx - off, 0.0) * float(getattr(case, 'csv_x_scale', 1.0) or 1.0)
    cr = cr / max(cr[0], 1e-9)
    k = cr >= runner.FLOOR_TRIM
    x, r = cx[k], cr[k] / cr[k][0]
    # janela pos-assentamento
    m = x > x[0] + 0.2 * (x[-1] - x[0])
    xs, rs = x[m], r[m]
    if len(xs) < 5:
        P('%-42s (curta demais)' % cid)
        continue
    xm = 0.5 * (xs[1:] + xs[:-1])
    rm = 0.5 * (rs[1:] + rs[:-1])
    taxa = -np.diff(rs) / np.maximum(np.diff(xs), 1e-9)
    ok = taxa > 1e-9
    mu = taxa[ok] / np.maximum(rm[ok], 1e-6)
    if ok.sum() < 4:
        P('%-42s (sem taxa positiva suficiente)' % cid)
        continue
    sl = float(np.polyfit(np.log10(xm[ok]), np.log10(mu), 1)[0])
    razao = float(np.median(mu[-3:]) / np.maximum(np.median(mu[:3]), 1e-12))
    F0 = case.initial_preload_N / 1e3
    out[cid] = dict(F0=F0, slope=sl, razao=razao)
    P('%-42s %8.0f %+10.2f %12.2f' % (cid[:42], F0, sl, razao))

P('')
P('ordenacao da subida (slope) nos 0,4 mm por F0 — Fig.5 preve 49 > 61 > 73:')
for cid in ['chu2026ti_D0p4mm_F0_49kN_test2', 'chu2026ti_D0p4mm_F0_61kN_test7',
            'chu2026ti_D0p4mm_F0_73kN_test8']:
    if cid in out:
        P('  F0=%2.0f kN: slope mu_impl %+0.2f' % (out[cid]['F0'], out[cid]['slope']))
json.dump(out, open('New_Theory/chu_mu_implicito.json', 'w'), indent=1)
P('-> New_Theory/chu_mu_implicito.json')
