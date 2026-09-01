"""Gates P1/P3/P5 do prereg 2026-07-28-ramp-capability (congelado em ea028ef).

P1 — paridade com a sonda A1: o FatigueLoss NATIVO (rampa opt-in), com relogio
     neutralizado (Goodman off via uts=1e30) e ancorado (fat_C1 tal que
     N_f = N_f(paper) exato), reproduz os cruzamentos da variante A1 da sonda
     A/B em +-1 ciclo nos 4 casos.
P3 — conservacao: |residual| <= 0.2 J com a rampa ativa (medido na sonda:
     0.017-0.151 J).
P5 — informacional (sem limiar): N_95 emergente do canonico vs Fig. 4.

P0/P2/P6 (inercia bit-a-bit nos 203 + LI_2022_TRIBOINT) rodam a parte, via
parallel_batch + comparacao de store (ver ramp_capability_resultado.md).

Uso: py -3.12 New_Theory/ramp_capability_gates.py
"""
import sys, json, pathlib
import numpy as np
sys.path.insert(0, str(pathlib.Path('src').resolve()))
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointMaterial)
from bolt_analysis_studio.validation import runner

H = {}
exec(compile(pathlib.Path('New_Theory/liu2025_ramp_v2_gates.py')
             .read_text(encoding='utf-8').split('P = print')[0], 'harness', 'exec'), H)

CORE = ['liu2025_M16_amp0p4', 'liu2025_M16_amp0p5', 'liu2025_M16_amp0p6']
FIG = 'liu2025_M16_fig2_single'
LEVELS = [0.80, 0.70, 0.60, 0.50, 0.40]
D_ON, Q = 0.75, 8.0
AB = json.load(open('New_Theory/liu2025_rampAB_result.json', encoding='utf-8'))

a = np.genfromtxt('New_Theory/liu2025_fig2_fine.csv', delimiter=',', skip_header=1)
fx, fr = a[:, 0], a[:, 1] / a[0, 1]
k = fr >= runner.FLOOR_TRIM
FINE = (fx[k], fr[k] / fr[k][0])


def sim_native(cid, ref):
    """Engine 100%% nativo: DynamicStiffnessAnalyzer default (FatigueLoss na
    lista default) com a rampa ligada por campos de JointMaterial."""
    rec, case, load, geom, kw, trim = H['build'](cid)
    nf = H['NF_PAPER'][cid]
    n_max = int(max(ref[0][-1], nf))
    delta = load['delta_mm'] * 1e-3
    sigma_a = geom.E * geom.d_2 * delta / max(geom.L_eff, 1e-6) ** 2  # Kt=1
    kw2 = dict(kw)
    kw2.update(fatigue_enabled=True, fat_stress_mode='bending', fat_Kt=1.0,
               fat_sigma_uts=1e30, fat_sigma_knee=0.0, fat_sigma_endurance=1.0,
               fat_m1=1.0, fat_C1=float(nf) * sigma_a,
               fat_ramp_D_on=D_ON, fat_ramp_q=Q)
    mat = JointMaterial(**kw2)
    ana = DynamicStiffnessAnalyzer(geom, mat, case.initial_preload_N)  # DEFAULT mechs
    F0 = case.initial_preload_N
    r = np.empty(n_max + 1)
    r[0] = 1.0
    for n in range(1, n_max + 1):
        ana.step_cycle(load['F_amp_N'], load['theta'], case.frequency_Hz,
                       delta_amp=delta)
        r[n] = max(ana.state.F_0, 0.0) / F0
    res = getattr(getattr(ana, 'energy', None), 'conservation_residual', None)
    if callable(res):
        res = res()
    return r, res


def crossings(r, ref):
    x, rd = ref
    n = len(r) - 1
    al = max(np.interp(float(x[0]), np.arange(n + 1), r), 1e-9)
    ya = r / al
    xs = np.arange(n + 1)
    out = {}
    for lvl in LEVELS:
        nd = H['crossing'](x, rd, lvl)
        nm = H['crossing'](xs, ya, lvl)
        out[lvl] = None if (nd is None or nm is None) else float(nm - nd)
    return out


P = print
P('=' * 78)
P('P1 + P3 — FatigueLoss NATIVO (rampa) vs sonda A1')
P('=' * 78)
p1_ok, p3_ok = True, True
det = {}
for cid in CORE + [FIG]:
    ref = FINE if cid == FIG else H['DATA'][cid]
    r, res = sim_native(cid, ref)
    cr = crossings(r, ref)
    a1 = {float(k_): v for k_, v in AB[cid]['A1']['cross'].items()}
    P('')
    P('%s   residual = %s J' % (cid, ('%.4g' % res) if res is not None else 'n/a'))
    P('  %8s %12s %12s %10s' % ('nivel', 'engine', 'sonda A1', 'delta'))
    worst = 0.0
    for lvl in LEVELS:
        e, s = cr.get(lvl), a1.get(lvl)
        if e is None or s is None:
            P('  %8.2f %12s %12s %10s' % (lvl, e, s, '--'))
            continue
        d = abs(e - s)
        worst = max(worst, d)
        P('  %8.2f %+12.0f %+12.0f %10.2f %s'
          % (lvl, e, s, d, 'ok' if d <= 1.0 else 'FORA <<<'))
        if d > 1.0:
            p1_ok = False
    if res is None or abs(res) > 0.2:
        p3_ok = False
    det[cid] = dict(residual=res, worst=worst,
                    cross={str(l): v for l, v in cr.items()})
P('')
P('  P1 (paridade +-1 ciclo) : %s' % ('OK' if p1_ok else 'FALHA'))
P('  P3 (|residual| <= 0.2 J): %s' % ('OK' if p3_ok else 'FALHA'))

# ------------------------------------------------------------------ P5 (info)
P('')
P('=' * 78)
P('P5 — INFORMACIONAL: N_95 emergente do CANONICO (store) vs Fig. 4')
P('=' * 78)
store = json.loads(pathlib.Path(
    'Models/CALIBRATION_AND_VALIDATION/validation_store.json')
    .read_text(encoding='utf-8'))
f4 = json.load(open('New_Theory/liu2025_fig4_DN.json', encoding='utf-8'))
n95_f4 = {round(d, 2): N for N, d in f4['M16']}
DELTA = {'liu2025_M16_amp0p25': 0.25, 'liu2025_M16_amp0p3': 0.30,
         'liu2025_M16_amp0p4': 0.40, 'liu2025_M16_amp0p5': 0.50,
         'liu2025_M16_amp0p6': 0.60, 'liu2025_M16_amp0p8': 0.80}
P('%8s %14s %14s %8s' % ('delta', 'N95 modelo', 'N95 fig4', 'razao'))
p5 = {}
for cid, d in DELTA.items():
    v = store[cid]
    cyc = np.asarray(v['cycles'], float)
    rat = np.asarray(v['ratio'], float)
    n95 = None
    for i in range(1, len(rat)):
        if rat[i] <= 0.95 < rat[i - 1]:
            t = (rat[i - 1] - 0.95) / max(rat[i - 1] - rat[i], 1e-12)
            n95 = float(cyc[i - 1] + t * (cyc[i] - cyc[i - 1]))
            break
    key = min(n95_f4, key=lambda x: abs(x - d))
    ref = n95_f4[key]
    p5[cid] = dict(model=n95, data=ref)
    P('%8.2f %14s %14.0f %8s'
      % (d, ('%.0f' % n95) if n95 else 'nunca', ref,
         ('%.2f' % (n95 / ref)) if n95 else '--'))
P('  (sem limiar; primeira medicao da fidelidade do relogio emergente N95;')
P('   resolucao do store ~n/400 ciclos; leitura VERTICAL no plato e mal-posta')
P('   em N — numeros sao ordem-de-grandeza, nao gate)')

json.dump(dict(P1=bool(p1_ok), P3=bool(p3_ok), detalhe=det, P5=p5),
          open('New_Theory/ramp_capability_result.json', 'w'), indent=1)
P('')
P('-> New_Theory/ramp_capability_result.json')
