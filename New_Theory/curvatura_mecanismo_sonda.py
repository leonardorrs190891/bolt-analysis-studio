"""Causa fisica do split: qual mecanismo carrega a perda CEDO vs TARDE em A e B."""
import sys, json
sys.path.insert(0, 'src')
import numpy as np
from collections import defaultdict
from bolt_analysis_studio.validation import report_html as rh
from bolt_analysis_studio.validation.case_registry import all_records
from bolt_analysis_studio.validation.runner import CaseResult

S = json.load(open('Models/CALIBRATION_AND_VALIDATION/validation_store.json', encoding='utf-8'))
recs = {r.case_id: r for r in all_records()}
res = {c: CaseResult.from_dict(S[c]) for c in S if c in recs}
pisos = rh._pisos_medidos([(recs[c].source, r) for c, r in res.items()])
MEC = ['embedding', 'creep', 'wear', 'rotational_loosening', 'thread_fretting', 'fatigue']

def fatias(r):
    """fatia de cada mecanismo no INCREMENTO do 1o e do ultimo terco."""
    d = r.decomp
    if not isinstance(d, dict) or not d: return None, None
    A = {k: np.asarray(d.get(k, []), float) for k in MEC}
    n = len(next(iter(A.values())))
    if n < 9: return None, None
    i1, i2 = n // 3, 2 * n // 3
    out = []
    for lo, hi in ((0, i1), (i2, n - 1)):
        inc = {k: abs(float(v[hi]) - float(v[lo])) for k, v in A.items() if len(v) == n}
        s = sum(inc.values()) or 1.0
        out.append({k: v / s for k, v in inc.items()})
    return out

grupo = defaultdict(list)
for c, r in res.items():
    f = recs[c].source
    if not rh.caso_comparavel(f, c) or r.mae is None: continue
    sd = rh.sres_para_censo(r)
    if sd is None: continue
    L = rh.limite_sres(f, pisos)
    if r.mae <= rh.META_MAE and r.maxerr <= rh.META_MAX and sd <= L: continue
    p = np.asarray(r.metric_pred, float); dd = np.asarray(r.metric_data, float)
    if len(p) < 9: continue
    t3 = [float(np.mean(z)) for z in np.array_split(p - dd, 3)]
    if not (max(t3) > 0 > min(t3)): continue
    if rh._perna_manda(r.mae, r.maxerr, sd, rh.META_MAE, rh.META_MAX, L) != 'sd': continue
    fa = fatias(r)
    if fa[0] is None: continue
    grupo['A' if t3[2] > t3[0] else 'B'].append((c, f, fa[0], fa[1]))

for g in ('A', 'B'):
    L_ = grupo[g]
    print('\n=== sub-classe %s — %d curvas ===' % (g, len(L_)))
    print('%-40s %s' % ('curva', '  '.join('%-9s' % m[:9] for m in ('emb', 'creep', 'wear', 'rotac', 'fret'))))
    for c, f, e, l in sorted(L_):
        cedo = '  '.join('%4.0f%%' % (100 * e.get(m, 0)) + '    ' for m in
                         ('embedding', 'creep', 'wear', 'rotational_loosening', 'thread_fretting'))
        print('%-40s %s' % (c[:40] + ' cedo', cedo))
        tarde = '  '.join('%4.0f%%' % (100 * l.get(m, 0)) + '    ' for m in
                          ('embedding', 'creep', 'wear', 'rotational_loosening', 'thread_fretting'))
        print('%-40s %s' % ('  tarde', tarde))
    print('  MEDIA cedo :', '  '.join('%s %.0f%%' % (m[:5], 100 * np.mean([e.get(m, 0) for _c, _f, e, _l in L_]))
                                      for m in MEC[:4]))
    print('  MEDIA tarde:', '  '.join('%s %.0f%%' % (m[:5], 100 * np.mean([l.get(m, 0) for _c, _f, _e, l in L_]))
                                      for m in MEC[:4]))
