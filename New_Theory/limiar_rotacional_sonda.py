import sys, json
sys.path.insert(0, 'src')
import numpy as np
from bolt_analysis_studio.validation import report_html as rh
from bolt_analysis_studio.validation.case_registry import all_records
from bolt_analysis_studio.validation.runner import CaseResult

S = json.load(open('Models/CALIBRATION_AND_VALIDATION/validation_store.json', encoding='utf-8'))
recs = {r.case_id: r for r in all_records()}
res = {c: CaseResult.from_dict(S[c]) for c in S if c in recs}
pisos = rh._pisos_medidos([(recs[c].source, r) for c, r in res.items()])

def rot(r):
    d = getattr(r, 'decomp', None)
    if not isinstance(d, dict) or not d: return None
    tot = {k: abs(float(np.asarray(v, float)[-1])) for k, v in d.items()}
    return tot.get('rotational_loosening', 0.0) / (sum(tot.values()) or 1.0)

def tri(f, r):
    L = rh.limite_sres(f, pisos); sd = rh.sres_para_censo(r)
    return r.mae <= rh.META_MAE and r.maxerr <= rh.META_MAX and sd is not None and sd <= L

vals = []
for c, r in res.items():
    f = recs[c].source
    if not rh.caso_comparavel(f, c) or r.mae is None: continue
    if tri(f, r): continue
    v = rot(r)
    if v is not None: vals.append((v, c))
vals.sort(reverse=True)

print('DISTRIBUICAO da fatia ROTACIONAL entre as %d fora do tripe' % len(vals))
print('(o classificador da bifurcacao corta em 70 % — e um degrau ou e arbitrario?)')
print()
for lo, hi in [(0.95,1.01),(0.90,0.95),(0.80,0.90),(0.70,0.80),(0.60,0.70),
               (0.50,0.60),(0.30,0.50),(0.10,0.30),(0.0,0.10)]:
    n = sum(1 for v, _ in vals if lo <= v < hi)
    bar = '#' * n
    print('  [%.2f, %.2f)  %2d  %s' % (lo, hi, n, bar))
print()
print('vizinhanca do corte de 0,70 — as 8 mais proximas dos dois lados:')
perto = sorted(vals, key=lambda z: abs(z[0] - 0.70))[:8]
for v, c in sorted(perto, reverse=True):
    print('   %6.3f  %-44s %s' % (v, c[:44], 'DENTRO (P-13)' if v >= 0.70 else 'fora do corte'))
arr = np.array([v for v, _ in vals])
janela = arr[(arr > 0.55) & (arr < 0.85)]
print()
print('curvas na faixa 0,55-0,85 (a zona onde o corte decide): %d' % len(janela))
if len(janela) > 1:
    g = np.diff(np.sort(janela))
    print('maior lacuna nessa faixa: %.3f  (lacuna grande => degrau natural;' % g.max())
    print('                              lacuna pequena => corte arbitrario)')
