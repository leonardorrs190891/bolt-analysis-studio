"""Premeasure: wear SATURANTE (superficie conforma => remove menos por ciclo).

d_wear *= 1/(1 + delta_wear_acumulado/W_sat)     (W_sat=inf => identico)

DISCRIMINANTE: tem de ajudar a sub-classe B e NAO ajudar a A. Se ajudar as duas,
e' botao generico, nao mecanismo.
"""
import sys, json
sys.path.insert(0, 'src')
import numpy as np
import bolt_analysis_studio.numerical.dynamic_stiffness_analyzer as dsa
import bolt_analysis_studio.validation.runner as rn
from bolt_analysis_studio.validation import report_html as rh
from bolt_analysis_studio.validation.case_registry import all_records, record
from bolt_analysis_studio.validation.runner import CaseResult

S = json.load(open('Models/CALIBRATION_AND_VALIDATION/validation_store.json', encoding='utf-8'))
recs = {r.case_id: r for r in all_records()}
res = {c: CaseResult.from_dict(S[c]) for c in S if c in recs}
pisos = rh._pisos_medidos([(recs[c].source, r) for c, r in res.items()])

B = ['eccles2010_fig7c_axial_2p7kN_constant', 'liu2025_M16_amp0p8',
     'eccles2010_fig7d_axial_3p1kN_constant', 'jcsr2023_stainless_seawater',
     'sun2025efa109235_transverse_grease_standard']
A = ['liu2025_M16_fig2_single', 'yang2019_M10_amp0p6_10Hz',
     'jcsr2023_plain_seawater', 'jcsr2023_galv_seawater']

_orig = dsa.WearLoss.rate
W = {'sat': 0.0}


def wrap(self, state, geom, mat, F_amp, theta_load, freq, cycle_N, **kw):
    out = _orig(self, state, geom, mat, F_amp, theta_load, freq, cycle_N, **kw)
    s = W['sat']
    if s <= 0.0:
        return out
    acc = float(getattr(state, 'delta_wear', 0.0) or 0.0)
    fac = 1.0 / (1.0 + acc / s)
    o = dict(out)
    for k in ('dF_0', 'dE_dissipated'):
        if k in o and isinstance(o[k], (int, float)):
            o[k] = o[k] * fac
    if isinstance(o.get('ds'), dict):
        o['ds'] = {k: v * fac for k, v in o['ds'].items()}
    return o


dsa.WearLoss.rate = wrap


def tri(f, r):
    sd = rh.sres_para_censo(r)
    return (r.mae <= rh.META_MAE and r.maxerr <= rh.META_MAX
            and sd is not None and sd <= rh.limite_sres(f, pisos))


for sat in (2e-6, 5e-6, 2e-5):
    W['sat'] = sat
    print('\n=== W_sat = %.0e m ===' % sat)
    print('%-42s %-3s %19s %19s %s' % ('curva', 'cls', 'ANTES', 'DEPOIS', ''))
    dB = dA = 0.0
    for c in B + A:
        if c not in res: continue
        a = res[c]
        try:
            r = rn.simulate_case(record(c))
        except Exception as ex:
            print('%-42s ERRO %s' % (c[:42], str(ex)[:38])); continue
        cls = 'B' if c in B else 'A'
        d = (a.resid_std - r.resid_std) / max(a.resid_std, 1e-9)
        if cls == 'B': dB += d
        else: dA += d
        print('%-42s %-3s %19s %19s  sd %+5.1f%% %s' % (
            c[:42], cls, '%.4f/%.4f/%.4f' % (a.mae, a.maxerr, a.resid_std),
            '%.4f/%.4f/%.4f' % (r.mae, r.maxerr, r.resid_std), 100 * d,
            'ENTRA' if tri(recs[c].source, r) and not tri(recs[c].source, a) else
            ('SAI' if tri(recs[c].source, a) and not tri(recs[c].source, r) else '')))
    print('  ganho medio de sigma:  B %+.1f%%   A %+.1f%%   %s' % (
        100 * dB / len(B), 100 * dA / len(A),
        'DISCRIMINA' if dB / len(B) > 0 and dB / len(B) > 2 * abs(dA / len(A)) else 'nao discrimina'))
