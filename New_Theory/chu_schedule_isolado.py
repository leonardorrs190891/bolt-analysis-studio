"""Contas de projeto pre-2a-tentativa do F3.2-CHU: o mu(N) MEDIDO, ISOLADO.

A 1a tentativa (2026-07-21, FAIL) embrulhou o schedule com a receita F3
(c_bend=1.881, C_creep=0, emb 1.6um, floors). Antes de gastar a ULTIMA
tentativa do prereg, medir o schedule ISOLADO sobre o estado adotado de HOJE
(sem chave per-rig = defaults):

  A) so mu_bearing_schedule (medido, Fig. 5)
  B) A + mu_thread=0.05 (input-de-paper)
  C) B + loose_arrest_floor lido (floors do f3_chu_result)

Criterio de decisao (G-CHU-a do prereg congelado): tripe <0,1 no test4 E
>=2 de {test2, test7, test8}. So gastar a tentativa se alguma variante
satisfizer nas contas.
"""
import sys, json, pathlib
import numpy as np
sys.path.insert(0, str(pathlib.Path('src').resolve()))
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointMaterial)
H = {}
exec(compile(pathlib.Path('New_Theory/liu2025_ramp_v2_gates.py')
             .read_text(encoding='utf-8').split('P = print')[0], 'harness', 'exec'), H)
from bolt_analysis_studio.validation.inputs import load_full_curve, repo_root
from bolt_analysis_studio.validation import runner
from bolt_analysis_studio.validation.case_registry import record

FIG5 = pathlib.Path('BAS_V2_papers/E. Rodada 4 (deep-research 2026-07-11)/digitized_csv')
ALVOS = {
    'chu2026ti_D0p4mm_F0_49kN_test2': ('test2', 0.11),
    'chu2026ti_D0p7mm_F0_49kN_test4': ('test4', 0.29),
    'chu2026ti_D0p4mm_F0_61kN_test7': ('test7', 0.18),
    'chu2026ti_D0p4mm_F0_73kN_test8': ('test8', 0.16),
}
STORE = json.loads(pathlib.Path(
    'Models/CALIBRATION_AND_VALIDATION/validation_store.json').read_text(encoding='utf-8'))

def schedule_de(tag):
    rows = [l.split(',') for l in
            (FIG5 / f'chu2026ti_fig5_muplate_{tag}.csv').read_text(encoding='utf-8')
            .strip().splitlines()[1:]]
    return tuple((float(a), float(b)) for a, b in rows)

def dado(cid):
    rec = record(cid); case = rec.validation_case
    cx, cr = load_full_curve(rec.csv_path.relative_to(repo_root()).as_posix())
    off = float(getattr(case, 'csv_x_offset', 0.0) or 0.0)
    cx = np.maximum(cx - off, 0.0) * float(getattr(case, 'csv_x_scale', 1.0) or 1.0)
    cr = cr / max(cr[0], 1e-9)
    k = cr >= runner.FLOOR_TRIM
    return cx[k], cr[k] / cr[k][0]

def sim_met(cid, extra):
    rec, case, load, geom, kw, _ = H['build'](cid)
    kw2 = dict(kw); kw2.update(extra)
    ana = DynamicStiffnessAnalyzer(geom, JointMaterial(**kw2), case.initial_preload_N)
    d = load['delta_mm'] * 1e-3
    x, rd = dado(cid)
    N = int(x[-1])
    r = np.empty(N + 1); r[0] = 1.0
    for n in range(1, N + 1):
        ana.step_cycle(load['F_amp_N'], load['theta'], case.frequency_Hz, delta_amp=d)
        ana.history.clear()
        r[n] = max(ana.state.F_0, 0.0) / case.initial_preload_N
    al = max(np.interp(float(x[0]), np.arange(N + 1), r), 1e-9)
    p = np.interp(x, np.arange(N + 1), r / al)
    e = np.abs(p - rd)
    return float(e.mean()), float(e.max())

P = print
P('%-8s %-14s' % ('curva', 'store'), '  '.join('%-16s' % v for v in ['A:sched', 'B:A+mu_th', 'C:B+floor']))
res = {}
for cid, (tag, floor) in ALVOS.items():
    sch = schedule_de(tag)
    variantes = {
        'A': dict(mu_bearing_schedule=sch),
        'B': dict(mu_bearing_schedule=sch, mu_thread=0.05),
        'C': dict(mu_bearing_schedule=sch, mu_thread=0.05, loose_arrest_floor=floor),
    }
    s = STORE[cid]
    row = []
    res[cid] = {}
    for nome, extra in variantes.items():
        m, x_ = sim_met(cid, extra)
        res[cid][nome] = [m, x_]
        row.append('%.3f/%.3f %s' % (m, x_, 'P' if (m <= .1 and x_ < .1) else 'F'))
    P('%-8s %-14s' % (tag, '%.3f/%.3f' % (s['mae'], s['maxerr'])),
      '  '.join('%-16s' % v for v in row))

P('')
for v in ['A', 'B', 'C']:
    ok4 = res['chu2026ti_D0p7mm_F0_49kN_test4'][v]
    ok4 = ok4[0] <= .1 and ok4[1] < .1
    n_out = sum(1 for c in ['chu2026ti_D0p4mm_F0_49kN_test2', 'chu2026ti_D0p4mm_F0_61kN_test7',
                            'chu2026ti_D0p4mm_F0_73kN_test8']
                if res[c][v][0] <= .1 and res[c][v][1] < .1)
    P('G-CHU-a com variante %s: test4 %s, outros %d/3  => %s'
      % (v, 'PASS' if ok4 else 'FAIL', n_out,
         'SATISFAZIVEL' if (ok4 and n_out >= 2) else 'nao satisfaz'))
json.dump(res, open('New_Theory/chu_schedule_isolado.json', 'w'), indent=1)
P('-> New_Theory/chu_schedule_isolado.json')
