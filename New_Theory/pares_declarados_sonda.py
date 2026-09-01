import sys, json
sys.path.insert(0, 'src')
import numpy as np
import bolt_analysis_studio.validation.runner as rn
from bolt_analysis_studio.validation import report_html as rh
from bolt_analysis_studio.validation.case_registry import all_records, record
from bolt_analysis_studio.validation.runner import CaseResult

S = json.load(open('Models/CALIBRATION_AND_VALIDATION/validation_store.json', encoding='utf-8'))
recs = {r.case_id: r for r in all_records()}
res = {c: CaseResult.from_dict(S[c]) for c in S if c in recs}
COND = ('c_bend', 'emb_depth', 'GA_member', 'd_hole_mm', 'd_washer_mm',
        'delta_free', 'k_tr_mode', 'conform_driver', 'mu_bearing', 'mu_thread',
        'C_creep', 'K_archard', 'k_wear_spec', 'flank_wear_on')

print('AUDITORIA dos %d PARES DECLARADOS' % len(rh._PARES_REPLICA_DECLARADOS))
print('(override manual da chave: afirmacao MAIS FORTE que a automatica)\n')
for a, b, rot in rh._PARES_REPLICA_DECLARADOS:
    if a not in res or b not in res:
        print('  %-34s FALTA no store' % (a[:34])); continue
    oa, ob = rn._effective_overrides(record(a), {}), rn._effective_overrides(record(b), {})
    dif = sorted(f for f in COND if str(oa.get(f)) != str(ob.get(f)))
    ca, cb = getattr(res[a], 'config_used', {}) or {}, getattr(res[b], 'config_used', {}) or {}
    dm = (ca.get('delta_mm'), cb.get('delta_mm'))
    fa = (ca.get('F_amp_N'), cb.get('F_amp_N'))
    # discordancia dado-vs-dado na janela comum
    xa = np.asarray(res[a].metric_x, float); ya = np.asarray(res[a].metric_data, float)
    xb = np.asarray(res[b].metric_x, float); yb = np.asarray(res[b].metric_data, float)
    lo, hi = max(xa.min(), xb.min()), min(xa.max(), xb.max())
    if hi > lo:
        g = np.linspace(lo, hi, 100)
        d = np.interp(g, xa, ya) - np.interp(g, xb, yb)
        piso = (float(np.mean(np.abs(d))), float(np.max(np.abs(d))), float(np.std(d)))
    else:
        piso = (float('nan'),) * 3
    print('  %-36s x %-36s' % (a[-36:], b[-36:]))
    print('     rotulo: %s' % rot[:96])
    print('     delta_mm %s   F_amp_N %s' % (dm, fa))
    print('     piso do par: MAE %.4f  mx %.4f  sd %.4f' % piso)
    print('     config divergente: %s' % (', '.join(dif) if dif else 'NENHUMA'))
    print()
