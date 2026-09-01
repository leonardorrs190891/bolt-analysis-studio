"""Contas PRE-CONGELAMENTO da rota E2 (N_f input-de-paper POR CURVA).

MEDE (entra no prereg):
  1. fat_C1 POR CURVA, ancorado para o relogio de Miner (Goodman VIVO) fraturar
     no N_f da matriz de ensaios — 2 passes de escala por curva. Os 7 valores
     ficam FIXADOS no prereg; a execucao nao fita nada.
  2. Residuo do relogio por curva apos ancoragem (deve ser ~exato).
  3. Tabela analitica D_trim = trim/N_f e alpha(D_trim) — a previsao central:
     com relogio exato, a rampa e' NUMERICAMENTE NULA em toda janela de metrica
     (alpha ~ 1e-6 na pior curva).
  4. Curva de PROJETO = amp0p8 (a que matou a adocao anterior): metrica
     pos-trim medida vs store.

NAO MEDE (cego p/ os gates): metrica pos-trim das outras 6 (trajetos
descartados sem avaliar); as 195 de fora.
"""
import sys, json, pathlib, time
import numpy as np
sys.path.insert(0, str(pathlib.Path('src').resolve()))
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointMaterial)

H = {}
exec(compile(pathlib.Path('New_Theory/liu2025_ramp_v2_gates.py')
             .read_text(encoding='utf-8').split('P = print')[0], 'harness', 'exec'), H)

NF = {'liu2025_M16_amp0p25': 330000.0, 'liu2025_M16_amp0p3': 250000.0,
      'liu2025_M16_amp0p4': 77000.0, 'liu2025_M16_amp0p5': 38000.0,
      'liu2025_M16_amp0p6': 24200.0, 'liu2025_M16_amp0p8': 14400.0,
      'liu2025_M16_fig2_single': 10000.0}
TRIM = {'liu2025_M16_amp0p25': 240000, 'liu2025_M16_amp0p3': 180000,
        'liu2025_M16_amp0p4': 60000, 'liu2025_M16_amp0p5': 30000,
        'liu2025_M16_amp0p6': 18000, 'liu2025_M16_amp0p8': 11500,
        'liu2025_M16_fig2_single': 8000}
# razoes N_pred/N_meas do C1 GLOBAL (contas da adocao) -> chute per-curva
R_GLOBAL = {'liu2025_M16_amp0p25': 1.259, 'liu2025_M16_amp0p3': 0.930,
            'liu2025_M16_amp0p4': 1.285, 'liu2025_M16_amp0p5': 1.302,
            'liu2025_M16_amp0p6': 1.361, 'liu2025_M16_amp0p8': 0.734,
            'liu2025_M16_fig2_single': 0.734}
C1_GLOBAL = 4.02544e32
M1, D_ON, Q, KT, UTS = 3.12, 0.75, 8.0, 0.588, 800e6
DESIGN = 'liu2025_M16_amp0p8'
P = print


def sim(cid, C1, n_cap, keep_traj=False):
    rec, case, load, geom, kw, _ = H['build'](cid)
    delta = load['delta_mm'] * 1e-3
    kw2 = dict(kw)
    kw2.update(fatigue_enabled=True, fat_stress_mode='bending', fat_Kt=KT,
               fat_sigma_uts=UTS, fat_sigma_knee=0.0, fat_sigma_endurance=1.0,
               fat_m1=M1, fat_C1=C1, fat_ramp_D_on=D_ON, fat_ramp_q=Q)
    ana = DynamicStiffnessAnalyzer(geom, JointMaterial(**kw2),
                                   case.initial_preload_N)
    F0 = case.initial_preload_N
    r = np.empty(n_cap + 1) if keep_traj else None
    if keep_traj:
        r[0] = 1.0
    nf = None
    for n in range(1, n_cap + 1):
        ana.step_cycle(load['F_amp_N'], load['theta'], case.frequency_Hz,
                       delta_amp=delta)
        rr = max(ana.state.F_0, 0.0) / F0
        if keep_traj:
            r[n] = rr
        if nf is None and rr <= 0.10:
            nf = n
            if not keep_traj:
                return float(nf), None
    return (float(nf) if nf else None), r


P('=' * 78)
P('CONTAS E2 — fat_C1 POR CURVA ancorado no N_f da matriz (input-de-paper)')
P('=' * 78)
C1S, resid = {}, {}
for cid, nfm in NF.items():
    c1 = C1_GLOBAL / R_GLOBAL[cid]
    for p in (1, 2):
        t0 = time.time()
        npred, _ = sim(cid, c1, int(1.35 * nfm))
        if npred is None:
            c1 *= 0.7
            P('  %-26s passe %d: nao fraturou em 1.35x — C1*0.7' % (cid, p))
            continue
        ratio = npred / nfm
        P('  %-26s passe %d (%3.0fs): N_pred %7.0f  razao %.4f'
          % (cid.split('M16_')[1], p, time.time() - t0, npred, ratio))
        if abs(ratio - 1.0) < 0.005:
            break
        c1 = c1 / ratio
    C1S[cid] = c1
    resid[cid] = ratio
P('')
P('C1 por curva (FIXADOS):')
for cid, v in C1S.items():
    P('  %-26s fat_C1 = %.6g   (relogio residual %.4f)'
      % (cid.split('M16_')[1], v, resid[cid]))

P('')
P('=' * 78)
P('3) previsao central: alpha da rampa NA BORDA DO TRIM (relogio exato)')
P('=' * 78)
P('%12s %10s %10s %10s %14s' % ('curva', 'trim', 'N_f', 'D_trim', 'alpha(D_trim)'))
for cid, nfm in NF.items():
    d = TRIM[cid] / nfm
    a = 0.0 if d <= D_ON else min(((d - D_ON) / (1 - D_ON)) ** Q, 1.0)
    P('%12s %10d %10.0f %10.4f %14.3g'
      % (cid.split('M16_')[1], TRIM[cid], nfm, d, a))
P('  => alpha <= ~3e-6 em toda janela: a rampa e NUMERICAMENTE NULA na metrica')

P('')
P('=' * 78)
P('4) CURVA DE PROJETO (%s) — pos-trim vs store' % DESIGN)
P('=' * 78)
nfm = NF[DESIGN]
npred, traj = sim(DESIGN, C1S[DESIGN], int(1.35 * nfm), keep_traj=True)
store = json.loads(pathlib.Path(
    'Models/CALIBRATION_AND_VALIDATION/validation_store.json')
    .read_text(encoding='utf-8'))
x, rd = H['DATA'][DESIGN]
m = x <= TRIM[DESIGN]
cd, rdd = x[m], rd[m]
n = len(traj) - 1
al = max(np.interp(float(cd[0]), np.arange(n + 1), traj), 1e-9)
pred = np.interp(cd, np.arange(n + 1), traj / al)
e = np.abs(pred - rdd)
mae, mx = float(e.mean()), float(e.max())
s = store[DESIGN]
P('  N_pred = %.0f (alvo %.0f, residual %.4f)' % (npred, nfm, npred / nfm))
P('  store: %.4f/%.4f  ->  com E2: %.4f/%.4f  (delta %+.5f/%+.5f)'
  % (s['mae'], s['maxerr'], mae, mx, mae - s['mae'], mx - s['maxerr']))
P('  tripe: %s' % ('PASSA' if (mae <= 0.10 and mx < 0.10) else 'FALHA'))

json.dump(dict(C1_per_case={k.split('M16_')[1]: v for k, v in C1S.items()},
               residuo_relogio={k.split('M16_')[1]: v for k, v in resid.items()},
               design=dict(cid=DESIGN, mae=mae, maxerr=mx,
                           base_mae=s['mae'], base_maxerr=s['maxerr'],
                           n_pred=npred)),
          open('New_Theory/liu2025_e2_contas.json', 'w'), indent=1)
P('-> New_Theory/liu2025_e2_contas.json')
