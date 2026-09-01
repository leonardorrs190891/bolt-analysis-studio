import sys, json
sys.path.insert(0, 'src')
import numpy as np
from collections import defaultdict
import bolt_analysis_studio.validation.runner as rn
from bolt_analysis_studio.validation import report_html as rh
from bolt_analysis_studio.validation.case_registry import all_records, record
from bolt_analysis_studio.validation.runner import CaseResult

S = json.load(open('Models/CALIBRATION_AND_VALIDATION/validation_store.json', encoding='utf-8'))
recs = {r.case_id: r for r in all_records()}
res = {c: CaseResult.from_dict(S[c]) for c in S if c in recs}
pares = [(recs[c].source, r) for c, r in res.items()]

SUSPEITAS = {'ECCLES_2010', 'LIU_2020_WEAR', 'LIU_2022_RETIGHT', 'SUN_2025_REASSY'}
COND = ('c_bend', 'emb_depth', 'GA_member', 'd_hole_mm', 'd_washer_mm',
        'delta_free', 'k_tr_mode', 'conform_driver', 'mu_bearing', 'mu_thread')

# membros das familias suspeitas (mesma chave do report)
grupos = defaultdict(list)
for cid, r in res.items():
    x, d = r.metric_x, r.metric_data
    if not (x and d and len(x) == len(d) >= 4): continue
    if cid in rh._SEM_FAMILIA_MECANICA: continue
    cfg = getattr(r, 'config_used', None) or {}
    try:
        k = (recs[cid].source, round(float(cfg.get('delta_mm') or 0), 4),
             round(float(cfg.get('F_amp_N') or 0), 1), cfg.get('mode'))
    except (TypeError, ValueError): continue
    grupos[k].append(cid)

alvo = set()
for k, cids in grupos.items():
    if k[0] not in SUSPEITAS or len(cids) < 2: continue
    ovs = {c: rn._effective_overrides(record(c), {}) for c in cids}
    if any(len({str(ovs[c].get(f)) for c in cids}) > 1 for f in COND):
        alvo |= set(cids)

p_hoje = rh._pisos_medidos(pares)
orig = rh._SEM_FAMILIA_MECANICA
try:
    rh._SEM_FAMILIA_MECANICA = set(orig) | alvo
    p_sem = rh._pisos_medidos(pares)
finally:
    rh._SEM_FAMILIA_MECANICA = orig

print('IMPACTO das 4 familias com condicao divergente (%d curvas)\n' % len(alvo))
print('%-18s %12s %12s   %s' % ('fonte', 'limite hoje', 'limite s/ ela', 'efeito'))
mudou = []
for f in sorted(SUSPEITAS):
    a, b = rh.limite_sres(f, p_hoje), rh.limite_sres(f, p_sem)
    print('%-18s %12.4f %12.4f   %s' % (f, a, b, 'APERTA' if b < a - 1e-9 else 'igual'))
    if b < a - 1e-9: mudou.append((f, a, b))

def passa(f, r, pis):
    L = rh.limite_sres(f, pis); sd = rh.sres_para_censo(r)
    return r.mae <= rh.META_MAE and r.maxerr <= rh.META_MAX and sd is not None and sd <= L

n_a = sum(1 for c, r in res.items()
          if rh.caso_comparavel(recs[c].source, c) and r.mae is not None
          and passa(recs[c].source, r, p_hoje))
n_b = sum(1 for c, r in res.items()
          if rh.caso_comparavel(recs[c].source, c) and r.mae is not None
          and passa(recs[c].source, r, p_sem))
print('\ncenso hoje %d  ·  censo com as 4 familias bloqueadas %d  ·  delta %+d' % (n_a, n_b, n_b - n_a))
if n_b != n_a:
    print('\ncurvas que passam SO POR CAUSA do piso inflado:')
    for c, r in sorted(res.items()):
        f = recs[c].source
        if not rh.caso_comparavel(f, c) or r.mae is None: continue
        if passa(f, r, p_hoje) and not passa(f, r, p_sem):
            print('   %-44s sigma %.4f  limite %.4f -> %.4f'
                  % (c[:44], r.resid_std, rh.limite_sres(f, p_hoje), rh.limite_sres(f, p_sem)))
