import sys, json
sys.path.insert(0, 'src')
import numpy as np
from bolt_analysis_studio.validation import report_html as rh
from bolt_analysis_studio.validation.case_registry import all_records
from bolt_analysis_studio.validation.runner import CaseResult

S = json.load(open('Models/CALIBRATION_AND_VALIDATION/validation_store.json', encoding='utf-8'))
recs = {r.case_id: r for r in all_records()}
res = {c: CaseResult.from_dict(S[c]) for c in S if c in recs}
pares = [(recs[c].source, r) for c, r in res.items()]

p_hoje = rh._pisos_medidos(pares)
orig = rh._PARES_REPLICA_DECLARADOS
try:
    rh._PARES_REPLICA_DECLARADOS = ()
    p_sem = rh._pisos_medidos(pares)
finally:
    rh._PARES_REPLICA_DECLARADOS = orig

fontes = sorted({recs[a].source for a, _b, _r in orig if a in recs})
print('IMPACTO dos 7 PARES DECLARADOS no limite da 3a perna\n')
print('%-20s %12s %12s   %s' % ('fonte', 'com pares', 'sem pares', 'efeito'))
for f in fontes:
    a, b = rh.limite_sres(f, p_hoje), rh.limite_sres(f, p_sem)
    ef = 'AFROUXA' if a > b + 1e-9 else ('aperta' if a < b - 1e-9 else 'igual')
    print('%-20s %12.4f %12.4f   %s' % (f, a, b, ef))

def passa(f, r, pis):
    L = rh.limite_sres(f, pis); sd = rh.sres_para_censo(r)
    return r.mae <= rh.META_MAE and r.maxerr <= rh.META_MAX and sd is not None and sd <= L

comp = [(c, r) for c, r in res.items()
        if rh.caso_comparavel(recs[c].source, c) and r.mae is not None]
n_a = sum(1 for c, r in comp if passa(recs[c].source, r, p_hoje))
n_b = sum(1 for c, r in comp if passa(recs[c].source, r, p_sem))
print('\ncenso com pares declarados %d  ·  sem eles %d  ·  delta %+d' % (n_a, n_b, n_b - n_a))
if n_a != n_b:
    print('\ncurvas que passam SO POR CAUSA de um par declarado:')
    for c, r in sorted(comp):
        f = recs[c].source
        if passa(f, r, p_hoje) and not passa(f, r, p_sem):
            print('   %-44s sigma %.4f  limite %.4f -> %.4f'
                  % (c[:44], r.resid_std, rh.limite_sres(f, p_hoje), rh.limite_sres(f, p_sem)))
