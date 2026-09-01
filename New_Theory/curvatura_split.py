import sys, json
sys.path.insert(0, 'src')
import numpy as np
from collections import Counter
from bolt_analysis_studio.validation import report_html as rh
from bolt_analysis_studio.validation.case_registry import all_records
from bolt_analysis_studio.validation.runner import CaseResult

S = json.load(open('Models/CALIBRATION_AND_VALIDATION/validation_store.json', encoding='utf-8'))
recs = {r.case_id: r for r in all_records()}
res = {c: CaseResult.from_dict(S[c]) for c in S if c in recs}
pisos = rh._pisos_medidos([(recs[c].source, r) for c, r in res.items()])

A, B = [], []
for c, r in res.items():
    f = recs[c].source
    if not rh.caso_comparavel(f, c) or r.mae is None: continue
    sd = rh.sres_para_censo(r)
    if sd is None: continue
    L = rh.limite_sres(f, pisos)
    if r.mae <= rh.META_MAE and r.maxerr <= rh.META_MAX and sd <= L: continue
    p = np.asarray(r.metric_pred, float); d = np.asarray(r.metric_data, float)
    if len(p) < 9: continue
    t3 = [float(np.mean(z)) for z in np.array_split(p - d, 3)]
    if not (max(t3) > 0 > min(t3)): continue
    if rh._perna_manda(r.mae, r.maxerr, sd, rh.META_MAE, rh.META_MAX, L) != 'sd': continue
    (A if t3[2] > t3[0] else B).append((c, f, t3, r, sd / L))

def bloco(rot, L_):
    print('\n=== %s — %d curvas ===' % (rot, len(L_)))
    print('%-42s %-16s %8s %8s %8s  %s' % ('curva', 'fonte', 'r1/3', 'r3/3', 'sd x', 'MAE/mx x'))
    for c, f, t3, r, sx in sorted(L_, key=lambda z: z[4]):
        print('%-42s %-16s %+8.4f %+8.4f %7.2fx  %.2f/%.2f' % (
            c[:42], f, t3[0], t3[2], sx, r.mae / rh.META_MAE, r.maxerr / rh.META_MAX))
    print('   fontes:', dict(Counter(f for _c, f, _t, _r, _s in L_)))

bloco('A — modelo RAPIDO cedo, DEVAGAR tarde  (residuo sobe)', A)
bloco('B — modelo DEVAGAR cedo, RAPIDO tarde  (residuo desce)', B)
print('\n=> as duas sub-classes tem sinal OPOSTO: uma forma unica nao pode servir as duas.')
