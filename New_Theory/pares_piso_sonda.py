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

# MESMA chave do report (copiada do sitio, nao reinventada): src, delta, F_amp, mode
grupos = defaultdict(list)
for cid, r in res.items():
    x = r.metric_x; d = r.metric_data
    if not (x and d and len(x) == len(d) >= 4): continue
    if cid in rh._SEM_FAMILIA_MECANICA: continue
    cfg = getattr(r, 'config_used', None) or {}
    try:
        k = (recs[cid].source, round(float(cfg.get('delta_mm') or 0), 4),
             round(float(cfg.get('F_amp_N') or 0), 1), cfg.get('mode'))
    except (TypeError, ValueError):
        continue
    grupos[k].append(cid)

# campos que codificam GEOMETRIA/CONDICAO (nao dispersao de especime)
COND = ('c_bend', 'emb_depth', 'GA_member', 'd_hole_mm', 'd_washer_mm',
        'delta_free', 'k_tr_mode', 'conform_driver', 'mu_bearing', 'mu_thread')
fam = {k: v for k, v in grupos.items() if len(v) >= 2}
print('familias automaticas com n>=2: %d  (chave: src, delta_mm, F_amp_N, mode)' % len(fam))
print('teste: membros com CONDICAO diferente nao sao replicas\n')
suspeitas = 0
for k in sorted(fam, key=lambda z: str(z)):
    cids = sorted(fam[k])
    ovs = {c: rn._effective_overrides(record(c), {}) for c in cids}
    dif = {f for f in COND if len({str(ovs[c].get(f)) for c in cids}) > 1}
    flag = 'SUSPEITA' if dif else 'ok'
    if dif: suspeitas += 1
    print('  %-46s n=%d  %-9s %s' % (str(k)[:46], len(cids), flag,
                                     (' difere: ' + ','.join(sorted(dif))) if dif else ''))
    if dif:
        for c in cids:
            print('        %-42s %s' % (c[:42], {f: ovs[c].get(f) for f in sorted(dif)}))
print('\nfamilias com condicao divergente: %d de %d' % (suspeitas, len(fam)))
