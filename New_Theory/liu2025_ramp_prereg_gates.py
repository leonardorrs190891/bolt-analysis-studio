"""Avaliacao PRE-EXECUCAO dos gates do prereg 2026-07-27 (liu2025-fracture-ramp).

Forma B1 do prereg:  A_eff/A_s = 1 - ((D - D_on)/(1 - D_on))^q
Knock-down:          g = (1-alpha)(1+rho)/((1-alpha)+rho),  rho = k_j/k_b
dF_0 por ciclo:      F_0 * (g_n/g_{n-1} - 1)

Dois RELOGIOS, para separar as duas afirmacoes que o prereg conflaciona:
  A) Miner do engine (D_fatigue), UMA (fat_C1, fat_m1)  <- o que o prereg propoe
  B) N_f LIDO da matriz de ensaios do artigo, por curva  <- isola a RAMPA
NAO toca codigo canonico: mecanismo injetado via loss_mechanisms.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path('src').resolve()))

import numpy as np
from scipy.optimize import brentq

from bolt_analysis_studio.validation import runner
from bolt_analysis_studio.validation.case_registry import record
from bolt_analysis_studio.validation.inputs import (load_full_curve, repo_root,
                                                    geometry_for_case)
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointMaterial, LossMechanism, EmbeddingLoss,
    CreepLoss, WearLoss, RotationalLooseningLoss, ThreadFrettingLoss,
    k_j_ax, sun_life)

# N_f DECLARADO na matriz de ensaios do artigo (apparatus_notes, "Cycles to end")
NF_PAPER = {'liu2025_M16_amp0p25': 330000.0, 'liu2025_M16_amp0p3': 250000.0,
            'liu2025_M16_amp0p4': 77000.0, 'liu2025_M16_amp0p5': 38000.0,
            'liu2025_M16_amp0p6': 24200.0, 'liu2025_M16_amp0p8': 14400.0,
            'liu2025_M16_fig2_single': 10000.0}
DELTA = {'liu2025_M16_amp0p25': 0.25, 'liu2025_M16_amp0p3': 0.30,
         'liu2025_M16_amp0p4': 0.40, 'liu2025_M16_amp0p5': 0.50,
         'liu2025_M16_amp0p6': 0.60, 'liu2025_M16_amp0p8': 0.80,
         'liu2025_M16_fig2_single': 0.80}
# tripe pos-trim de HOJE (store 4f5bedfbace4): MAE / maxerr / sigma_res
TODAY = {'liu2025_M16_amp0p25': (0.0757, 0.0945, 0.0267),
         'liu2025_M16_amp0p3': (0.0645, 0.0865, 0.0249),
         'liu2025_M16_amp0p4': (0.0462, 0.0623, 0.0203),
         'liu2025_M16_amp0p5': (0.0291, 0.0516, 0.0184),
         'liu2025_M16_amp0p6': (0.0228, 0.0650, 0.0201),
         'liu2025_M16_amp0p8': (0.0487, 0.0853, 0.0302),
         'liu2025_M16_fig2_single': (0.0389, 0.0546, 0.0224)}
CIDS = list(NF_PAPER)


class RampLoss(LossMechanism):
    """B1 do prereg. mat._ramp = (D_on, q, clock, nf) ; clock in {'miner','paper'}"""
    name = "fatigue"

    def rate(self, state, geom, mat, F_amp, theta_load, freq, cycle_N,
             slip_amp_override=None, delta_amp=None):
        cfg = getattr(mat, "_ramp", None)
        if cfg is None or state.F_0 <= 0.0:
            return dict(dF_0=0.0, dE_dissipated=0.0, ds={})
        D_on, q, clock, nf = cfg
        if clock == 'paper':
            D0 = min(max((cycle_N - 1) / nf, 0.0), 1.0)
            D1 = min(cycle_N / nf, 1.0)
            dD = D1 - D0
        else:
            A_s = max(geom.A_s, 1e-9)
            if mat.fat_stress_mode == "bending" and delta_amp is not None:
                L = max(geom.L_eff, 1e-6)
                sa = mat.fat_Kt * geom.E * geom.d_2 * max(delta_amp, 0.0) / (L * L)
            else:
                sa = mat.fat_Kt * abs(F_amp) / A_s
            sm = max(state.F_0, 0.0) / A_s
            den = max(1.0 - sm / max(mat.fat_sigma_uts, 1.0), 1e-3)
            N_f = sun_life(sa / den, mat)
            dD = (1.0 / N_f) if np.isfinite(N_f) and N_f > 0.0 else 0.0
            D0 = min(max(state.D_fatigue, 0.0), 1.0)
            D1 = min(D0 + dD, 1.0)
        if D_on is None:                       # relogio puro (sem rampa)
            return dict(dF_0=0.0, dE_dissipated=0.0, ds=dict(D_fatigue=dD))
        rho = k_j_ax(state, mat) / max(geom.k_b, 1e-9)

        def g(D):
            if D <= D_on:
                return 1.0
            a = min(((D - D_on) / (1.0 - D_on)) ** q, 1.0)
            if a >= 1.0:
                return 0.0
            return ((1.0 - a) / ((1.0 - a) + rho)) * (1.0 + rho)

        g0, g1 = g(D0), g(D1)
        dF = max(state.F_0, 0.0) * (g1 / max(g0, 1e-12) - 1.0)
        return dict(dF_0=min(dF, 0.0), dE_dissipated=0.0,
                    ds=dict(D_fatigue=dD))


_c = {}


def build(cid, extra=None):
    if cid not in _c:
        rec = record(cid)
        case = rec.validation_case
        load = runner._loading_for(rec)
        inp = load['inputs']
        geom = geometry_for_case(case, grip_mm=inp['grip_mm']['value'],
                                 E=(inp.get('E') or {}).get('value'))
        geom = runner._apply_adopted_geometry(geom, rec.source, rec.case_id,
                                            case.bolt_size)
        _c[cid] = (rec, case, load, geom, runner.material_kwargs_for(rec, inp))
    rec, case, load, geom, kw0 = _c[cid]
    kw = dict(kw0); kw.update(extra or {})
    return rec, case, load, geom, JointMaterial(**kw)


def sim(cid, n_max, ramp=None, extra=None):
    rec, case, load, geom, mat = build(cid, extra)
    object.__setattr__(mat, '_ramp', ramp)
    ana = DynamicStiffnessAnalyzer(
        geom, mat, case.initial_preload_N,
        loss_mechanisms=[EmbeddingLoss(), CreepLoss(), WearLoss(),
                         RotationalLooseningLoss(), ThreadFrettingLoss(),
                         RampLoss()])
    d = load['delta_mm'] * 1e-3 if load['mode'] == 'displacement' else None
    F0 = case.initial_preload_N
    r = np.empty(n_max + 1); r[0] = 1.0
    for n in range(1, n_max + 1):
        ana.step_cycle(load['F_amp_N'], load['theta'], case.frequency_Hz,
                       delta_amp=d)
        r[n] = max(ana.state.F_0, 0.0) / F0
    return r, ana


DATA = {}
for cid in CIDS:
    rec = record(cid)
    cx, cr = load_full_curve(rec.csv_path.relative_to(repo_root()).as_posix())
    cr = cr / cr[0]
    k = cr >= runner.FLOOR_TRIM
    cx, cr = cx[k], cr[k]
    DATA[cid] = (cx, cr / cr[0])


def met(r, cid):
    cx, cr = DATA[cid]
    n = len(r) - 1
    m = cx <= n
    cd, rd = cx[m], cr[m]
    al = max(np.interp(float(cd[0]), np.arange(n + 1), r), 1e-9)
    p = np.interp(cd, np.arange(n + 1), r / al)
    e = np.abs(p - rd)
    return float(e.mean()), float(e.max()), float(np.std(p - rd))


print('=' * 79)
print('0) DADO DE GATE (registrado, sem _tozero, apos FLOOR_TRIM=0.10)')
print('=' * 79)
print('%-24s %7s %9s %8s %8s' % ('case', 'n_pts', 'N_fim', 'r_fim', 'N_f_paper'))
for cid in CIDS:
    cx, cr = DATA[cid]
    print('%-24s %7d %9.0f %8.3f %9.0f' % (cid, len(cx), cx[-1], cr[-1],
                                           NF_PAPER[cid]))

print()
print('  (relogio A / Miner ja medido no probe2: erro de N_f -13.8/-34.6/-7.4/')
print('   +0.0/+3.6/-34.4/-5.5 %%; PR-24 com m1=2.7 + escala global: ~17%% max)')
print()
print('=' * 79)
print('2) RELOGIO B (N_f LIDO do artigo) — isola a RAMPA. Grade (D_on, q)')
print('=' * 79)
GRID = [(0.75, 2.0), (0.75, 3.0), (0.80, 2.0), (0.80, 3.0), (0.80, 5.0),
        (0.85, 3.0), (0.85, 5.0)]
res = {}
print('%-24s %-9s' % ('case', 'hoje') + ' '.join('%13s' % ('%.2f/q=%.0f' % g) for g in GRID))
for cid in CIDS:
    cx, cr = DATA[cid]
    n_max = int(cx[-1])
    row = []
    for (Don, q) in GRID:
        r, ana = sim(cid, n_max, ramp=(Don, q, 'paper', NF_PAPER[cid]))
        m = met(r, cid)
        row.append(m)
        res[(cid, Don, q)] = (m, float(r[-1]))
    t = TODAY[cid]
    print('%-24s %-9s' % (cid, '%.3f/%.3f' % (t[0], t[1]))
          + ' '.join('%13s' % ('%.3f/%.3f' % (m[0], m[1])) for m in row))

print()
print('  MAE/res.max na curva INTEIRA (sem trim). "hoje" = tripe POS-trim.')
print()
print('=' * 79)
print('3) GATES do prereg, avaliados')
print('=' * 79)
for (Don, q) in GRID:
    g1 = res[('liu2025_M16_fig2_single', Don, q)][0]
    ok1 = g1[0] <= 0.10 and g1[1] < 0.10 and g1[2] <= TODAY['liu2025_M16_fig2_single'][2]
    g2a = res[('liu2025_M16_amp0p25', Don, q)][0]
    g2b = res[('liu2025_M16_amp0p3', Don, q)][0]
    ok2 = (g2a[0] <= TODAY['liu2025_M16_amp0p25'][0] + 0.01 and g2a[1] < 0.10
           and g2b[0] <= TODAY['liu2025_M16_amp0p3'][0] + 0.01 and g2b[1] < 0.10)
    trip = sum(1 for c in CIDS
               if res[(c, Don, q)][0][0] <= 0.10 and res[(c, Don, q)][0][1] < 0.10)
    print('  D_on=%.2f q=%.0f | G1(fig2) %s (%.3f/%.3f/%.4f) | G2 %s | tripe %d/7'
          % (Don, q, 'OK ' if ok1 else 'FAIL', g1[0], g1[1], g1[2],
             'OK ' if ok2 else 'FAIL', trip))

print()
print('=' * 79)
print('4) G4 — a perda de secao atravessa o loose_arrest_floor=0.25?')
print('=' * 79)
Don, q = 0.80, 3.0
for cid in ['liu2025_M16_fig2_single', 'liu2025_M16_amp0p5']:
    cx, _ = DATA[cid]
    r, _ = sim(cid, int(cx[-1]), ramp=(Don, q, 'paper', NF_PAPER[cid]))
    r0, _ = sim(cid, int(cx[-1]), ramp=None)
    print('  %-24s r_fim: sem rampa %.3f | com rampa %.3f  (floor=0.250)'
          % (cid, r0[-1], r[-1]))
print('  => se "com rampa" < 0.250, a perda de secao PASSA POR BAIXO do arresto.')

print()
print('=' * 79)
print('5) G5 — discriminancia: as celulas passam SEM o candidato?')
print('=' * 79)
for cid in CIDS:
    cx, _ = DATA[cid]
    r0, _ = sim(cid, int(cx[-1]), ramp=None)
    m0 = met(r0, cid)
    print('  %-24s SEM rampa (inteira): MAE %.3f  res.max %.3f  %s'
          % (cid, m0[0], m0[1], 'passa tripe' if (m0[0] <= .1 and m0[1] < .1) else 'FALHA tripe'))
