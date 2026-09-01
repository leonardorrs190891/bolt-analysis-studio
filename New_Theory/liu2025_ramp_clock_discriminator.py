"""DISCRIMINADOR DE RELOGIO — o joelho do Liu2025 e' cronometrado por
   (a) trabalho de slip acumulado (relogio dos canais wear/dano), ou
   (b) vida de fadiga D-N (relogio de tensao alternada)?

Teste: o expoente da lei N_joelho ~ delta^-q.
  - relogio de slip-work: W/ciclo ~ mu*F0*slip ~ delta  =>  q ~ 1
  - relogio de fadiga:    N_f = C*sigma_a^-m, sigma_a ~ delta  =>  q ~ m (~3)
Mede-se o slip e o W_slip do PROPRIO engine, sem supor nada.

Depois: teste de COLAPSO — o fator extra que falta, f = r_dado/r_modelo,
colapsa numa unica funcao de D=N/N_f para as 6 amplitudes?
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path('src').resolve()))

import numpy as np
from bolt_analysis_studio.validation import runner
from bolt_analysis_studio.validation.case_registry import record, all_records
from bolt_analysis_studio.validation.inputs import load_full_curve, repo_root

# N_f fisico (fim do ensaio/fratura). Onde existe a variante _tozero ela da o
# fim real; nas outras o ultimo ponto e' o limite do grafico (~2% antes).
NF = {'liu2025_M16_amp0p25': 327000.0, 'liu2025_M16_amp0p3': 252000.0,
      'liu2025_M16_amp0p4': 78000.0, 'liu2025_M16_amp0p5': 38000.0,
      'liu2025_M16_amp0p6': 24200.0, 'liu2025_M16_amp0p8': 14400.0,
      'liu2025_M16_fig2_single': 10000.0}
DELTA = {'liu2025_M16_amp0p25': 0.25, 'liu2025_M16_amp0p3': 0.30,
         'liu2025_M16_amp0p4': 0.40, 'liu2025_M16_amp0p5': 0.50,
         'liu2025_M16_amp0p6': 0.60, 'liu2025_M16_amp0p8': 0.80}

CIDS = [r.case_id for r in all_records() if 'liu2025' in r.case_id.lower()]

print('=' * 78)
print('A) RELOGIO DE SLIP-WORK medido no engine (W_slip_acc por ciclo)')
print('=' * 78)
print('%-24s %6s %10s %12s %12s' % ('case', 'delta', 'slip_um', 'W_slip/cyc_J', 'N p/ W=250kJ'))
rows = []
sims = {}
for cid in CIDS:
    rec = record(cid)
    res = runner.simulate_case(rec)
    sims[cid] = res
    # re-roda ~2000 ciclos so p/ ler o estado interno
    from bolt_analysis_studio.validation.inputs import (frozen_constants,
                                                        geometry_for_case,
                                                        emb_depth_vdi)
    from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
        DynamicStiffnessAnalyzer, JointMaterial)
    case = rec.validation_case
    load = runner._loading_for(rec)
    inp = load['inputs']
    geom = geometry_for_case(case, grip_mm=inp['grip_mm']['value'],
                             E=(inp.get('E') or {}).get('value'))
    geom = runner._apply_adopted_geometry(geom, rec.source, rec.case_id,
                                          case.bolt_size)
    mat = JointMaterial(**runner.material_kwargs_for(rec, inp))
    ana = DynamicStiffnessAnalyzer(geom, mat, case.initial_preload_N)
    d_amp = load['delta_mm'] * 1e-3 if load['mode'] == 'displacement' else None
    NPROBE = 2000
    W0 = 0.0
    for n in range(NPROBE):
        ana.step_cycle(load['F_amp_N'], load['theta'], case.frequency_Hz,
                       delta_amp=d_amp)
    W = ana.state.W_slip_acc
    wpc = W / NPROBE
    slip = ana.history[-1].slip_amp if hasattr(ana.history[-1], 'slip_amp') else float('nan')
    n_for = 250000.0 / wpc if wpc > 0 else float('inf')
    d = DELTA.get(cid, load['delta_mm'])
    print('%-24s %6.2f %10.2f %12.4g %12.4g' % (cid, d, slip * 1e6 if slip == slip else -1, wpc, n_for))
    if cid in DELTA:
        rows.append((d, wpc))

if len(rows) >= 3:
    dd = np.array([r[0] for r in rows]); ww = np.array([r[1] for r in rows])
    ok = ww > 0
    if ok.sum() >= 3:
        p, c = np.polyfit(np.log(dd[ok]), np.log(ww[ok]), 1)
        print()
        print('  W_slip/ciclo ~ delta^%+.3f  =>  relogio de slip-work da N_joelho ~ delta^%+.3f' % (p, -p))
    else:
        print('\n  W_slip/ciclo = 0 em %d das %d amplitudes (regime partial-slip):' % ((~ok).sum(), len(dd)))
        print('  o relogio de slip-work NAO EXISTE nessas curvas — nunca dispara.')

amps = np.array([DELTA[c] for c in CIDS if c in DELTA])
nfs = np.array([NF[c] for c in CIDS if c in DELTA])
q, c = np.polyfit(np.log(amps), np.log(nfs), 1)
print()
print('  DADO:  N_f ~ delta^%+.3f   (R2 log = %.4f)' % (
    q, 1 - ((np.log(nfs) - (c + q * np.log(amps))) ** 2).sum()
    / ((np.log(nfs) - np.log(nfs).mean()) ** 2).sum()))
print('  => expoente compativel com relogio de FADIGA (m~3), nao de slip-work (q~1).')

print()
print('=' * 78)
print('B) TESTE DE COLAPSO: f = r_dado/r_modelo em funcao de D = N/N_f')
print('=' * 78)
grid = np.array([0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 0.98, 1.00])
print('%-24s' % 'D =' + ' '.join('%7.2f' % g for g in grid))
tab = []
for cid in CIDS:
    res = sims[cid]
    rec = record(cid)
    rel = rec.csv_path.relative_to(repo_root()).as_posix()
    cx, cr = load_full_curve(rel)
    cr = cr / cr[0]
    keep = cr >= runner.FLOOR_TRIM
    cx, cr = cx[keep], cr[keep]
    cr = cr / cr[0]
    cyc = np.array(res.cycles); ratio = np.array(res.ratio)
    al = max(np.interp(float(cx[0]), cyc, ratio), 1e-9)
    D = cx / NF[cid]
    f = cr / np.interp(cx, cyc, ratio / al)
    fg = np.interp(grid, D, f, left=np.nan, right=np.nan)
    print('%-24s' % cid + ' '.join('%7.3f' % v for v in fg))
    tab.append(fg)
tab = np.array(tab)
print('%-24s' % 'media' + ' '.join('%7.3f' % v for v in np.nanmean(tab, axis=0)))
print('%-24s' % 'desvio' + ' '.join('%7.3f' % v for v in np.nanstd(tab, axis=0)))
