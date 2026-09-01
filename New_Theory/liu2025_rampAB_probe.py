"""Sonda A-vs-B para a rampa de fratura (estudo liu2025_estudo_curvas.md §5).

Mede, em vez de argumentar, o trade-off entre:
  A0: rampa aplica dF_0 direto, dE=0 (a sonda dos gates v2 — referencia de regressao)
  A1: A0 + energetica por incremento (dE = U_before - U_after, estilo cliff)
  B1: A1 + k_b MODULADO por A_eff (a "perda de secao entra no [K(s)]")

ANALISE ESTRUTURAL PREVIA (a validar aqui): neste carregamento (transversal,
disp-mode), o feedback "F0 cai -> mais slip -> mais wear" corre por state.F_0
(F_slip = mu*F0) e existe nas DUAS opcoes. O que B acrescenta:
  (i)  dF_0 = -k_b*d_delta dos OUTROS mecanismos fica menor (k_b baixo) -> sinal
       NEGATIVO (amortece o colapso);
  (ii) Phi = k_b/(k_b+kj) cai -> menos parcela axial -> ~inerte aqui;
  (iii) k_tr (bending) usa d_2^4, NAO k_b -> slip transversal NAO ve k_b;
  (iv) U_internal usa k_b -> bookkeeping.
Previsao registrada ANTES de rodar: A1 ~ B1 na forma da curva (diferencas de 2a
ordem, B levemente MAIS LENTO no fim), residual de A0 pior que A1/B1.

Engine canonico NAO tocado. Nada adotado.
"""
import sys, json, pathlib
import numpy as np
sys.path.insert(0, str(pathlib.Path('src').resolve()))
from dataclasses import replace, fields
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial, LossMechanism,
    EmbeddingLoss, CreepLoss, WearLoss, RotationalLooseningLoss,
    ThreadFrettingLoss, U_internal, k_j_ax)
from bolt_analysis_studio.validation import runner

# arnes dos gates v2 (build/DATA/NF/tol/crossing) — reuso por exec do cabecalho
H = {}
exec(compile(pathlib.Path('New_Theory/liu2025_ramp_v2_gates.py')
             .read_text(encoding='utf-8').split('P = print')[0], 'harness', 'exec'), H)

CORE = ['liu2025_M16_amp0p4', 'liu2025_M16_amp0p5', 'liu2025_M16_amp0p6']
FIG = 'liu2025_M16_fig2_single'
D_ON, Q = 0.75, 8.0                      # par vencedor do prereg v2
LEVELS = [0.80, 0.70, 0.60, 0.50, 0.40]
TOL = {c: H['tol'](c) for c in CORE}
TOL[FIG] = 300.0                          # 0.15 * (10000-8000), prereg v2

# fig2 FINO como referencia (unico colapso completo)
a = np.genfromtxt('New_Theory/liu2025_fig2_fine.csv', delimiter=',', skip_header=1)
fx, fr = a[:, 0], a[:, 1] / a[0, 1]
k = fr >= runner.FLOOR_TRIM
FINE = (fx[k], fr[k] / fr[k][0])


def alpha_of(D):
    if D <= D_ON:
        return 0.0
    return min(((D - D_ON) / (1.0 - D_ON)) ** Q, 1.0)


class RampLoss(LossMechanism):
    """B1 do prereg v1, relogio LIDO (D = N/NF). mat._ramp=(nf, with_dE)."""
    name = "fatigue"

    def rate(self, state, geom, mat, F_amp, theta_load, freq, cycle_N,
             slip_amp_override=None, delta_amp=None):
        nf, with_dE = mat._ramp
        if state.F_0 <= 0.0:
            return dict(dF_0=0.0, dE_dissipated=0.0, ds={})
        D0 = min(max((cycle_N - 1) / nf, 0.0), 1.0)
        D1 = min(cycle_N / nf, 1.0)
        rho = k_j_ax(state, mat) / max(geom.k_b, 1e-9)

        def g(D):
            al = alpha_of(D)
            if al >= 1.0:
                return 0.0
            return ((1.0 - al) / ((1.0 - al) + rho)) * (1.0 + rho)

        g0, g1 = g(D0), g(D1)
        dF = min(max(state.F_0, 0.0) * (g1 / max(g0, 1e-12) - 1.0), 0.0)
        dE = 0.0
        if with_dE and dF < 0.0:
            U0 = U_internal(state, geom, mat)
            U1 = U_internal(replace(state, F_0=max(state.F_0 + dF, 0.0)),
                            geom, mat)
            dE = max(U0 - U1, 0.0)
        return dict(dF_0=dF, dE_dissipated=dE, ds=dict(D_fatigue=D1 - D0))


class GeomB(JointGeometry):
    """Geometria com k_b modulado por A_eff (Opcao B). _aeff setado por ciclo."""
    _aeff = 1.0

    @property
    def k_b(self):
        return JointGeometry.k_b.fget(self) * max(self._aeff, 1e-6)


def sim(cid, variant, ref):
    rec, case, load, geom0, kw, trim = H['build'](cid)
    nf = H['NF_PAPER'][cid]
    n_max = int(max(ref[0][-1], nf))
    mat = JointMaterial(**kw)
    object.__setattr__(mat, '_ramp', (nf, variant != 'A0'))
    geom = geom0
    if variant == 'B1':
        geom = GeomB(**{f.name: getattr(geom0, f.name)
                        for f in fields(geom0) if f.init})
    ana = DynamicStiffnessAnalyzer(
        geom, mat, case.initial_preload_N,
        loss_mechanisms=[EmbeddingLoss(), CreepLoss(), WearLoss(),
                         RotationalLooseningLoss(), ThreadFrettingLoss(),
                         RampLoss()])
    d = load['delta_mm'] * 1e-3 if load['mode'] == 'displacement' else None
    F0 = case.initial_preload_N
    r = np.empty(n_max + 1)
    r[0] = 1.0
    mech_win = {}
    n_win = int(D_ON * nf)
    for n in range(1, n_max + 1):
        if variant == 'B1':
            geom._aeff = 1.0 - alpha_of(min(n / nf, 1.0))
        ana.step_cycle(load['F_amp_N'], load['theta'], case.frequency_Hz,
                       delta_amp=d)
        r[n] = max(ana.state.F_0, 0.0) / F0
        if n >= n_win:
            for mech, dF in ana.history[-1].dF_0_by_mech.items():
                mech_win[mech] = mech_win.get(mech, 0.0) + dF
    res = getattr(getattr(ana, 'energy', None), 'conservation_residual', None)
    if callable(res):
        res = res()
    return r, mech_win, res


def crossings(r, cid, ref):
    x, rd = ref
    n = len(r) - 1
    al = max(np.interp(float(x[0]), np.arange(n + 1), r), 1e-9)
    ya = r / al
    xs = np.arange(n + 1)
    out = {}
    for lvl in LEVELS:
        nd = H['crossing'](x, rd, lvl)
        nm = H['crossing'](xs, ya, lvl)
        out[lvl] = (None if nd is None else
                    (None if nm is None else float(nm - nd)))
    return out


P = print
P('=' * 78)
P('SONDA A0 / A1 / B1 — rampa de fratura, nucleo + fig2 fino')
P('=' * 78)
resumo = {}
for cid in CORE + [FIG]:
    ref = FINE if cid == FIG else H['DATA'][cid]
    P('')
    P('%s  (tol %.0f ciclos)' % (cid, TOL[cid]))
    P('  %-4s %8s %10s %s' % ('var', 'r_fim', 'residual',
                              ' '.join('%9s' % ('d@%.2f' % l) for l in LEVELS)))
    for var in ('A0', 'A1', 'B1'):
        r, mech, res = sim(cid, var, ref)
        cr = crossings(r, cid, ref)
        ok = sum(1 for l, v in cr.items()
                 if v is not None and abs(v) <= TOL[cid])
        tot = sum(1 for v in cr.values() if v is not None)
        resumo.setdefault(cid, {})[var] = dict(
            r_fim=float(r[-1]), residual=(None if res is None else float(res)),
            cross={str(l): v for l, v in cr.items()}, ok=ok, tot=tot,
            mech_win={m: float(v) for m, v in mech.items()})
        P('  %-4s %8.3f %10s %s   %d/%d' % (
            var, r[-1],
            ('%.3g' % res) if res is not None else 'n/a',
            ' '.join(('%+9.0f' % v) if v is not None else '%9s' % '--'
                     for v in cr.values()), ok, tot))
    # delta B1-A1 por mecanismo na janela da rampa
    mA = resumo[cid]['A1']['mech_win']
    mB = resumo[cid]['B1']['mech_win']
    P('  janela da rampa (N>=%.2f*NF), dF_0 acumulado por mecanismo [kN]:' % D_ON)
    for m in sorted(set(mA) | set(mB)):
        a_, b_ = mA.get(m, 0.0) / 1e3, mB.get(m, 0.0) / 1e3
        P('    %-22s A1 %+9.3f   B1 %+9.3f   (B-A %+8.3f)' % (m, a_, b_, b_ - a_))

json.dump(resumo, open('New_Theory/liu2025_rampAB_result.json', 'w'), indent=1)
P('')
P('-> New_Theory/liu2025_rampAB_result.json')
