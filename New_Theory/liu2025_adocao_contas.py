"""Contas de satisfazibilidade PRE-CONGELAMENTO do prereg de adocao LIU_2025.

Roda ANTES de escrever os gates (regra §4.47/§4.48: conta RODADA, cobrindo o
pior caso do escopo). O que ESTE script mede e o que deliberadamente NAO mede:

  MEDE  (entra no prereg como conta):
    1. fat_Kt per-rig: razao entre a transferencia linear da Table 2
       (c_sigma = 1081 MPa/mm, M16) e o proxy de flexao do engine (Kt=1).
    2. fat_C1 ANCORADO nas 6 vidas de fratura medidas, no contexto canonico
       (Goodman VIVO), por 2 passes de escala geometrica. C1 fica FIXADO no
       prereg — na execucao da adocao NADA e fitado.
    3. Espalhamento do relogio com o C1 unico (razao N_pred/N_meas por curva).
    4. Tabela rampa-inicio (0.75*N_pred) vs trim_n_max — o risco central.
    5. Metrica pos-trim da CURVA DE PROJETO (amp0p4, a mais arriscada: rampa
       entra ~2k ciclos DENTRO da janela da metrica) vs baseline do store.

  NAO MEDE (fica CEGO para os gates da execucao):
    - metrica pos-trim das outras 6 curvas (os trajetos nao sao avaliados nem
      persistidos alem de N_pred);
    - qualquer numero das 195 curvas de fora.

Engine canonico ja contem a capacidade (f05a531); nada e adotado aqui.
"""
import sys, json, pathlib, time
import numpy as np
sys.path.insert(0, str(pathlib.Path('src').resolve()))
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointMaterial)
from bolt_analysis_studio.validation import runner

H = {}
exec(compile(pathlib.Path('New_Theory/liu2025_ramp_v2_gates.py')
             .read_text(encoding='utf-8').split('P = print')[0], 'harness', 'exec'), H)

# vidas de fratura MEDIDAS (matriz de ensaios; fig2 EXCLUIDO da ancora — a
# amplitude dele nao e reportada no artigo, errata §4.48b)
NF = {'liu2025_M16_amp0p25': 330000.0, 'liu2025_M16_amp0p3': 250000.0,
      'liu2025_M16_amp0p4': 77000.0, 'liu2025_M16_amp0p5': 38000.0,
      'liu2025_M16_amp0p6': 24200.0, 'liu2025_M16_amp0p8': 14400.0}
TRIM = {'liu2025_M16_amp0p25': 240000, 'liu2025_M16_amp0p3': 180000,
        'liu2025_M16_amp0p4': 60000, 'liu2025_M16_amp0p5': 30000,
        'liu2025_M16_amp0p6': 18000, 'liu2025_M16_amp0p8': 11500}
M1, D_ON, Q = 3.12, 0.75, 8.0
C_SIGMA = 1081e6 / 1e-3          # Pa por METRO de delta (1081 MPa/mm, Table 2)
UTS_88 = 800e6                    # classe 8.8, d<=16 (handbook)
DESIGN = 'liu2025_M16_amp0p4'

P = print
P('=' * 78)
P('CONTAS PRE-CONGELAMENTO — adocao per-rig LIU_2025 (fadiga+rampa)')
P('=' * 78)

# ---------------------------------------------------------- 1) fat_Kt per-rig
rec, case, load, geom, kw, _ = H['build'](DESIGN)
proxy = geom.E * geom.d_2 / max(geom.L_eff, 1e-6) ** 2      # Pa/m com Kt=1
KT = C_SIGMA / proxy
P('')
P('1) fat_Kt = c_sigma(Table2) / proxy_flexao = %.4g / %.4g = %.3f'
  % (C_SIGMA, proxy, KT))
P('   (sigma_a passa a SER a tensao de raiz do artigo; per-rig via Table 2)')


def sim_frac(cid, C1, n_cap):
    """Simula ate fraturar (r<=0.10) ou n_cap; devolve (N_frac|None, r_traj?)."""
    rec, case, load, geom, kw, _ = H['build'](cid)
    delta = load['delta_mm'] * 1e-3
    kw2 = dict(kw)
    kw2.update(fatigue_enabled=True, fat_stress_mode='bending', fat_Kt=KT,
               fat_sigma_uts=UTS_88, fat_sigma_knee=0.0,
               fat_sigma_endurance=1.0, fat_m1=M1, fat_C1=C1,
               fat_ramp_D_on=D_ON, fat_ramp_q=Q)
    ana = DynamicStiffnessAnalyzer(geom, JointMaterial(**kw2),
                                   case.initial_preload_N)
    F0 = case.initial_preload_N
    r = np.empty(n_cap + 1)
    r[0] = 1.0
    nf = None
    for n in range(1, n_cap + 1):
        ana.step_cycle(load['F_amp_N'], load['theta'], case.frequency_Hz,
                       delta_amp=delta)
        r[n] = max(ana.state.F_0, 0.0) / F0
        if nf is None and r[n] <= 0.10:
            nf = n
            if cid != DESIGN:
                return float(nf), None          # cego: trajeto descartado
    return (float(nf) if nf else None), r


# --------------------------------------------- 2) ancora de C1 em 2 passes
# chute inicial: regressao N=1.557e13*sigma_MPa^-3.12 em unidades do engine,
# corrigida grosseiramente pelo Goodman inicial (denom0^m1)
sigma0_MPa = C_SIGMA * 0.4e-3 / 1e6              # 0.4 mm de referencia
C1_regr = 1.557e13 * (1e6) ** M1                 # Pa, sem Goodman
denom0 = 1.0 - (60e3 / geom.A_s) / UTS_88
C1 = C1_regr / denom0 ** M1                      # Goodman encurta -> C1 desce? nao:
# sigma_ar = sigma/denom > sigma => N cai por denom^m1; para MANTER N, C1 sobe:
C1 = C1_regr * (1.0 / denom0) ** M1
P('')
P('2) ancora de fat_C1 (2 passes, contexto canonico, Goodman VIVO)')
P('   chute: C1_regr(Pa) = %.4g ; denom0 = %.4f ; C1_0 = %.4g'
  % (C1_regr, denom0, C1))
for p in (1, 2):
    t0 = time.time()
    ratios = {}
    for cid, nf_m in NF.items():
        n_cap = int(1.8 * nf_m)
        nf_p, _ = sim_frac(cid, C1, n_cap)
        ratios[cid] = (nf_p / nf_m) if nf_p else None
    ok = [v for v in ratios.values() if v]
    gm = float(np.exp(np.mean(np.log(ok)))) if ok else float('nan')
    P('   passe %d (%.0fs): N_pred/N_meas = %s | geomean %.3f'
      % (p, time.time() - t0,
         {k.split('amp')[1]: (round(v, 3) if v else 'nao-frat')
          for k, v in ratios.items()}, gm))
    if p == 1:
        C1 = C1 / gm                             # N ~ C1 => corrige pela geomean
        P('   C1 corrigido -> %.6g' % C1)
P('   >>> fat_C1 FIXADO = %.6g  (unico escalar fitado; congelado no prereg)' % C1)

# ------------------------------------------ 3/4) espalhamento + rampa vs trim
P('')
P('3/4) relogio final + rampa-inicio (0.75*N_pred) vs trim_n_max')
P('%10s %10s %10s %8s %12s %10s %s'
  % ('delta', 'N_meas', 'N_pred', 'razao', 'rampa@', 'trim', 'rampa vs janela'))
res3 = {}
r_design = None
for cid, nf_m in NF.items():
    n_cap = int(1.8 * nf_m)
    nf_p, rr = sim_frac(cid, C1, n_cap)
    if cid == DESIGN:
        r_design = rr
    ramp0 = D_ON * nf_p if nf_p else None
    res3[cid] = dict(N_meas=nf_m, N_pred=nf_p, ramp0=ramp0)
    tag = ('DENTRO da metrica (%.0f ciclos)' % (TRIM[cid] - ramp0)
           if ramp0 and ramp0 < TRIM[cid] else 'fora da metrica')
    P('%10s %10.0f %10s %8s %12s %10d %s'
      % (cid.split('M16_')[1], nf_m,
         ('%.0f' % nf_p) if nf_p else 'nao-frat',
         ('%.3f' % (nf_p / nf_m)) if nf_p else '--',
         ('%.0f' % ramp0) if ramp0 else '--', TRIM[cid], tag))

# --------------------------------------- 5) curva de projeto: metrica pos-trim
P('')
P('5) CURVA DE PROJETO (%s) — metrica pos-trim vs store' % DESIGN)
store = json.loads(pathlib.Path(
    'Models/CALIBRATION_AND_VALIDATION/validation_store.json')
    .read_text(encoding='utf-8'))
x, rd = H['DATA'][DESIGN]
m = x <= TRIM[DESIGN]
cd, rdd = x[m], rd[m]
n = len(r_design) - 1
al = max(np.interp(float(cd[0]), np.arange(n + 1), r_design), 1e-9)
pred = np.interp(cd, np.arange(n + 1), r_design / al)
e = np.abs(pred - rdd)
mae, mx = float(e.mean()), float(e.max())
s = store[DESIGN]
P('   store (sem fadiga): MAE %.4f  res.max %.4f' % (s['mae'], s['maxerr']))
P('   com adocao        : MAE %.4f  res.max %.4f   (delta %+.4f / %+.4f)'
  % (mae, mx, mae - s['mae'], mx - s['maxerr']))
P('   tripe pos-trim: %s' % ('PASSA' if (mae <= 0.10 and mx < 0.10) else 'FALHA'))

json.dump(dict(fat_Kt=KT, fat_C1=C1, fat_m1=M1, D_on=D_ON, q=Q, uts=UTS_88,
               relogio=res3, design=dict(cid=DESIGN, mae=mae, maxerr=mx,
                                         base_mae=s['mae'], base_maxerr=s['maxerr'])),
          open('New_Theory/liu2025_adocao_contas.json', 'w'), indent=1)
P('')
P('-> New_Theory/liu2025_adocao_contas.json')
