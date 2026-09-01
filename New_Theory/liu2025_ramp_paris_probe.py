"""PROBE 2 (nao-canonico): acoplamento FADIGA -> COMPLIANCE, medido.

(1) relogio: N em que D_fatigue cruza 1, SEM matar F_0 (clock-only)
(2) sweep de R: MAE/maxerr na curva INTEIRA (sem trim) vs baseline
(3) trim residual necessario apos a forma
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

NF = {'liu2025_M16_amp0p25': 327000.0, 'liu2025_M16_amp0p3': 252000.0,
      'liu2025_M16_amp0p4': 78000.0, 'liu2025_M16_amp0p5': 38000.0,
      'liu2025_M16_amp0p6': 24200.0, 'liu2025_M16_amp0p8': 14400.0,
      'liu2025_M16_fig2_single': 10000.0}
DELTA = {'liu2025_M16_amp0p25': 0.25, 'liu2025_M16_amp0p3': 0.30,
         'liu2025_M16_amp0p4': 0.40, 'liu2025_M16_amp0p5': 0.50,
         'liu2025_M16_amp0p6': 0.60, 'liu2025_M16_amp0p8': 0.80,
         'liu2025_M16_fig2_single': 0.80}
TRIM = {'liu2025_M16_amp0p25': 240000.0, 'liu2025_M16_amp0p3': 180000.0,
        'liu2025_M16_amp0p4': 60000.0, 'liu2025_M16_amp0p5': 30000.0,
        'liu2025_M16_amp0p6': 18000.0, 'liu2025_M16_amp0p8': 11500.0,
        'liu2025_M16_fig2_single': 8000.0}
CIDS = list(NF)


class FatComp(LossMechanism):
    """FatigueLoss + acoplamento continuo D_fatigue -> secao -> F_0.
    mat._fat_R <= 1  => degrau (comportamento canonico atual)
    mat._fat_clock_only  => so acumula D (nao toca F_0): mede o relogio"""
    name = "fatigue"

    def rate(self, state, geom, mat, F_amp, theta_load, freq, cycle_N,
             slip_amp_override=None, delta_amp=None):
        if not mat.fatigue_enabled:
            return dict(dF_0=0.0, dE_dissipated=0.0, ds={})
        clock_only = getattr(mat, "_fat_clock_only", False)
        if state.F_0 <= 0.0 and not clock_only:
            return dict(dF_0=0.0, dE_dissipated=0.0, ds={})
        A_s = max(geom.A_s, 1e-9)
        if mat.fat_stress_mode == "bending" and delta_amp is not None:
            L = max(geom.L_eff, 1e-6)
            sigma_a = mat.fat_Kt * geom.E * geom.d_2 * max(delta_amp, 0.0) / (L * L)
        else:
            sigma_a = mat.fat_Kt * abs(F_amp) / A_s
        sigma_m = max(state.F_0, 0.0) / A_s
        denom = max(1.0 - sigma_m / max(mat.fat_sigma_uts, 1.0), 1e-3)
        N_f = sun_life(sigma_a / denom, mat)
        dD = (1.0 / N_f) if np.isfinite(N_f) and N_f > 0.0 else 0.0
        if clock_only:
            return dict(dF_0=0.0, dE_dissipated=0.0, ds=dict(D_fatigue=dD))
        D0 = min(max(state.D_fatigue, 0.0), 1.0)
        D1 = min(D0 + dD, 1.0)
        R = getattr(mat, "_fat_R", 0.0)
        if R <= 1.0:                                    # degrau canonico
            if D1 >= 1.0:
                F_res = mat.fatigue_residual_frac * max(state.F_0_init, 0.0)
                return dict(dF_0=-(max(state.F_0, 0.0) - F_res),
                            dE_dissipated=0.0, ds=dict(D_fatigue=dD))
            return dict(dF_0=0.0, dE_dissipated=0.0, ds=dict(D_fatigue=dD))
        beta = max(mat.fat_m1 / 2.0 - 1.0, 1e-3)
        rho = k_j_ax(state, mat) / max(geom.k_b, 1e-9)

        def g(D):
            if D >= 1.0:
                return 0.0
            base = max(R - (R - 1.0) * D, 1e-12)
            alpha = min(base ** (-2.0 / beta), 1.0)
            return ((1.0 - alpha) / ((1.0 - alpha) + rho)) * (1.0 + rho)

        g0, g1 = g(D0), g(D1)
        dF_0 = max(state.F_0, 0.0) * (g1 / max(g0, 1e-12) - 1.0)
        return dict(dF_0=min(dF_0, 0.0), dE_dissipated=0.0,
                    ds=dict(D_fatigue=dD))


_cache = {}


def build(cid, extra=None):
    if cid not in _cache:
        rec = record(cid)
        case = rec.validation_case
        load = runner._loading_for(rec)
        inp = load['inputs']
        geom = geometry_for_case(case, grip_mm=inp['grip_mm']['value'],
                                 E=(inp.get('E') or {}).get('value'))
        geom = runner._apply_adopted_geometry(geom, rec.source, rec.case_id,
                                             case.bolt_size)
        _cache[cid] = (rec, case, load, geom, runner.material_kwargs_for(rec, inp))
    rec, case, load, geom, kw0 = _cache[cid]
    kw = dict(kw0); kw.update(extra or {})
    return rec, case, load, geom, JointMaterial(**kw)


def simulate(cid, extra, n_max, fat_R=0.0, clock_only=False, track_D=False):
    rec, case, load, geom, mat = build(cid, extra)
    object.__setattr__(mat, '_fat_R', fat_R)
    object.__setattr__(mat, '_fat_clock_only', clock_only)
    ana = DynamicStiffnessAnalyzer(
        geom, mat, case.initial_preload_N,
        loss_mechanisms=[EmbeddingLoss(), CreepLoss(), WearLoss(),
                         RotationalLooseningLoss(), ThreadFrettingLoss(),
                         FatComp()])
    d_amp = load['delta_mm'] * 1e-3 if load['mode'] == 'displacement' else None
    F0 = case.initial_preload_N
    r = np.empty(n_max + 1); r[0] = 1.0
    Dh = np.zeros(n_max + 1) if track_D else None
    for n in range(1, n_max + 1):
        ana.step_cycle(load['F_amp_N'], load['theta'], case.frequency_Hz,
                       delta_amp=d_amp)
        r[n] = max(ana.state.F_0, 0.0) / F0
        if track_D:
            Dh[n] = ana.state.D_fatigue
    return r, ana, Dh


def data_of(cid):
    rec = record(cid)
    rel = rec.csv_path.relative_to(repo_root()).as_posix()
    cx, cr = load_full_curve(rel)
    cr = cr / cr[0]
    keep = cr >= runner.FLOOR_TRIM
    cx, cr = cx[keep], cr[keep]
    return cx, cr / cr[0]


def metrics(r, cx, cr, upto=None):
    n = len(r) - 1
    m = cx <= (upto if upto is not None else n)
    m &= cx <= n
    cd, rd = cx[m], cr[m]
    if len(cd) == 0:
        return None
    al = max(np.interp(float(cd[0]), np.arange(n + 1), r), 1e-9)
    pred = np.interp(cd, np.arange(n + 1), r / al)
    e = np.abs(pred - rd)
    k = int(np.argmax(e))
    return dict(mae=float(e.mean()), maxerr=float(e[k]), at=float(cd[k]),
                std=float(np.std(pred - rd)), n=len(cd), pred=pred, data=rd, x=cd)


# ------------------------------------------------------ ancoras da lei de vida
amps = np.array([DELTA[c] for c in CIDS if c != 'liu2025_M16_fig2_single'])
nfs = np.array([NF[c] for c in CIDS if c != 'liu2025_M16_fig2_single'])
m_slope, lc = np.polyfit(np.log(amps), np.log(nfs), 1)
M1 = -m_slope
BASE_FAT = dict(fatigue_enabled=True, fat_stress_mode='bending', fat_m1=M1,
                fat_sigma_uts=800e6, fat_sigma_knee=1.0,
                fat_sigma_endurance=0.0)
ANCHOR = 'liu2025_M16_amp0p5'


def D_at_end(logC1, cid, cap):
    ex = dict(BASE_FAT, fat_C1=10 ** logC1)
    _, ana, _ = simulate(cid, ex, cap, clock_only=True)
    return ana.state.D_fatigue


logC1 = brentq(lambda L: D_at_end(L, ANCHOR, int(NF[ANCHOR])) - 1.0,
               10.0, 45.0, xtol=1e-5)
C1 = 10 ** logC1
FAT = dict(BASE_FAT, fat_C1=C1)
print('=' * 78)
print('1) RELOGIO DE FADIGA — 2 constantes, ancoradas na D-N do artigo')
print('=' * 78)
print('  fat_m1 = %.3f  (= -slope da D-N medida; LIDO, invariante a escala)' % M1)
print('  fat_C1 = %.4g  (ancorado em N_f=%.0f na amplitude %.2f mm; 1 fit)'
      % (C1, NF[ANCHOR], DELTA[ANCHOR]))
print()
print('  N em que D_fatigue cruza 1 (clock-only, Goodman VIVO), zero refit:')
print('  %-24s %6s %9s %9s %8s' % ('case', 'delta', 'N_f_med', 'N_f_mod', 'err%'))
for cid in CIDS:
    cap = int(NF[cid] * 1.6)
    _, ana, Dh = simulate(cid, FAT, cap, clock_only=True, track_D=True)
    idx = np.argmax(Dh >= 1.0)
    nmod = float(idx) if Dh[-1] >= 1.0 else float('nan')
    print('  %-24s %6.2f %9.0f %9.0f %+8.1f' % (
        cid, DELTA[cid], NF[cid], nmod, 100 * (nmod / NF[cid] - 1)))

# ------------------------------------------------------------------ sweep de R
print()
print('=' * 78)
print('2) SWEEP DE R (1 constante nova) — metrica na curva INTEIRA (sem trim)')
print('=' * 78)
DATA = {cid: data_of(cid) for cid in CIDS}
RS = [0.0, 8.0, 11.0, 14.0, 18.0, 25.0]
base = {}
print('%-24s %-12s' % ('case', 'R=') + ' '.join('%13s' % ('%.0f' % r if r else 'baseline')
                                                for r in RS))
for cid in CIDS:
    cx, cr = DATA[cid]
    n_max = int(cx[-1])
    out = []
    for R in RS:
        ex = FAT if R > 0 else {}
        r, _, _ = simulate(cid, ex, n_max, fat_R=R)
        mt = metrics(r, cx, cr)
        out.append(mt)
        if R == 0.0:
            base[cid] = mt
    print('%-24s %-12s' % (cid, 'MAE/max')
          + ' '.join('%13s' % ('%.3f/%.3f' % (o['mae'], o['maxerr'])) for o in out))

print()
print('  (baseline R=0 = FatigueLoss como esta hoje: degrau em D=1, sem joelho)')
