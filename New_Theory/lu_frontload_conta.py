"""Contas de satisfazibilidade da forma (b) do Lu: afrouxamento FRONT-LOADED.

Fila (correcao de escopo 2026-07-27): "o Lu pede taxa front-loaded (decai
desde o ciclo 1) — NUNCA testada; nada no canal de afrouxamento decai com a
rotacao acumulada". Linha N_emb fechada hoje (gate FAIL 2x: amp0p25 piora
sob a regra de feature).

Forma candidata: fator f = theta0 / (theta0 + theta_acc) no canal rotacional
(decaimento hiperbolico com a rotacao acumulada; theta0 -> inf = OFF).
Emulacao SEM engine: monkeypatch em RotationalLooseningLoss.rate escalando
dF_0/dE/d_theta por f(state.theta_loose).

Desenho anti-FAIL1 (transferencia INTRA-fonte, criterio da fila):
  ancora = fig18 (varredura de AMPLITUDE, 5 curvas) -> 1D em theta0
  cegas  = fig20 (varredura de TORQUE, 5 curvas) -> zero-refit
Regua: PR-37' (nenhum caso pior +0.01; mediana MAE da fonte -30% ou <=0.05).
"""
import sys, json, pathlib, statistics
import numpy as np
sys.path.insert(0, str(pathlib.Path('src').resolve()))
from bolt_analysis_studio.validation import runner
from bolt_analysis_studio.validation.case_registry import all_records
from bolt_analysis_studio.numerical import dynamic_stiffness_analyzer as dsa

recs = {r.case_id: r for r in all_records() if r.source == 'LU_2024'}
FIG18 = sorted(c for c in recs if 'fig18' in c)
FIG20 = sorted(c for c in recs if 'fig20' in c)
STORE = json.loads(pathlib.Path('Models/CALIBRATION_AND_VALIDATION/validation_store.json')
                   .read_text(encoding='utf-8'))

_orig_rate = dsa.RotationalLooseningLoss.rate
_TH0 = [None]  # None = OFF

def _patched(self, state, geom, mat, *a, **kw):
    out = _orig_rate(self, state, geom, mat, *a, **kw)
    th0 = _TH0[0]
    if th0 is None or th0 <= 0:
        return out
    f = th0 / (th0 + max(getattr(state, 'theta_loose', 0.0), 0.0))
    out = dict(out)
    for k in ('dF_0', 'dE_dissipated'):
        if k in out:
            out[k] = out[k] * f
    ds = dict(out.get('ds', {}))
    if 'theta_loose' in ds:
        ds['theta_loose'] = ds['theta_loose'] * f
        out['ds'] = ds
    return out

def sim(cid, th0):
    _TH0[0] = th0
    try:
        return runner.simulate_case(recs[cid])
    finally:
        _TH0[0] = None

P = print
dsa.RotationalLooseningLoss.rate = _patched
try:
    P('1) controle negativo (patch OFF) na fig18_amp0p5:')
    r = sim('lu2024_M8_fig18_amp0p5', None)
    s = STORE['lu2024_M8_fig18_amp0p5']
    P('   %.4f/%.4f vs store %.4f/%.4f  delta %.1e/%.1e'
      % (r.mae, r.maxerr, s['mae'], s['maxerr'], abs(r.mae - s['mae']), abs(r.maxerr - s['maxerr'])))

    P('2) ancora: varredura 1D de theta0 [rad] na fig18 (mediana MAE das 5)')
    melhor = None
    for th0 in [0.002, 0.005, 0.01, 0.02, 0.05, 0.1]:
        maes = [sim(c, th0).mae for c in FIG18]
        med = statistics.median(maes)
        P('   theta0=%.3f -> mediana MAE fig18 = %.4f' % (th0, med))
        if melhor is None or med < melhor[1]:
            melhor = (th0, med)
    th0 = melhor[0]
    P('   ancora: theta0=%.3f (mediana %.4f; store fig18 mediana %.4f)'
      % (th0, melhor[1], statistics.median(STORE[c]['mae'] for c in FIG18)))

    P('3) fonte inteira com a ancora (fig20 = zero-refit cego):')
    res = {}
    for c in FIG18 + FIG20:
        r = sim(c, th0)
        res[c] = (r.mae, r.maxerr)
        s = STORE[c]
        pior = r.mae > s['mae'] + 0.01 or r.maxerr > s['maxerr'] + 0.01
        P('   %-28s %.3f/%.3f -> %.3f/%.3f %s%s%s'
          % (c.replace('lu2024_M8_', ''), s['mae'], s['maxerr'], r.mae, r.maxerr,
             'CEGO ' if c in FIG20 else '', 'PIOR!' if pior else 'ok',
             ' TRIPE' if (r.mae <= .1 and r.maxerr < .1) else ''))
    m0 = statistics.median(STORE[c]['mae'] for c in res)
    m1 = statistics.median(v[0] for v in res.values())
    piores = [c for c in res if res[c][0] > STORE[c]['mae'] + 0.01
              or res[c][1] > STORE[c]['maxerr'] + 0.01]
    P('')
    P('mediana MAE fonte: %.4f -> %.4f (%+.1f%%) | piores: %s'
      % (m0, m1, 100 * (m1 / m0 - 1), piores or 'nenhum'))
    P('PR-37: %s' % ('SATISFAZIVEL' if (not piores and (m1 <= m0 * 0.7 or m1 <= 0.05)) else 'NAO satisfaz'))
finally:
    dsa.RotationalLooseningLoss.rate = _orig_rate
json.dump({c: list(v) for c, v in res.items()}, open('New_Theory/lu_frontload_conta.json', 'w'), indent=1)
P('-> New_Theory/lu_frontload_conta.json')
