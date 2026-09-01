"""Sonda de FORMA: wear ENERGETICO (mu-acoplado) no Chu, com mu(t) MEDIDO.

Fato medido hoje (chu_schedule_isolado): prescrever o mu(t) da Fig. 5 e quase
inerte (|delta| ~0.01) — porque o wear do engine e Archard (K/H * p * slip),
SEM mu, e o wear carrega 93% da perda do Chu. O mecanismo que o paper MEDE
(F0 -> COF -> taxa de afrouxamento) nao tem alavanca na lei de wear atual.

Forma candidata (nivel de LEI): d_wear = k_E * mu_eff(t) * p * slip
(wear energetico; V1 tem 'energy' como wear_model_type, V2 nao).

Emulacao SEM tocar o engine: k_wear_spec e lido do mat a cada ciclo ->
mutar mat.k_wear_spec = k_E * mu_sched(n) por ciclo reproduz a lei
bit-exatamente. mu(t) = input de MEDICAO (Fig. 5); k_E = 1 constante per-rig.

Protocolo anti-FAIL1 (licao do kernel-A): ancorar onde o mecanismo esta
ATIVO — k_E fitado 1D no test4 (curva de projeto) — e transferir ZERO-REFIT
para test2/7/8 (cegas). Criterio: o G-CHU-a do prereg F3.2 (test4 <0.1 no
tripe E >=2 de {2,7,8}) como regua de satisfazibilidade para um prereg NOVO.
"""
import sys, json, pathlib
import numpy as np
sys.path.insert(0, str(pathlib.Path('src').resolve()))
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointMaterial)
H = {}
exec(compile(pathlib.Path('New_Theory/liu2025_ramp_v2_gates.py')
             .read_text(encoding='utf-8').split('P = print')[0], 'harness', 'exec'), H)
from bolt_analysis_studio.validation.inputs import load_full_curve, repo_root
from bolt_analysis_studio.validation import runner
from bolt_analysis_studio.validation.case_registry import record

FIG5 = pathlib.Path('BAS_V2_papers/E. Rodada 4 (deep-research 2026-07-11)/digitized_csv')
ALVOS = ['chu2026ti_D0p7mm_F0_49kN_test4',       # ancora (1D em k_E)
         'chu2026ti_D0p4mm_F0_49kN_test2',       # cegas (zero-refit)
         'chu2026ti_D0p4mm_F0_61kN_test7',
         'chu2026ti_D0p4mm_F0_73kN_test8']
TAG = {c: c.split('_')[-1] for c in ALVOS}
STORE = json.loads(pathlib.Path(
    'Models/CALIBRATION_AND_VALIDATION/validation_store.json').read_text(encoding='utf-8'))

def mu_de(tag):
    rows = [l.split(',') for l in
            (FIG5 / f'chu2026ti_fig5_muplate_{tag}.csv').read_text(encoding='utf-8')
            .strip().splitlines()[1:]]
    xs = np.array([float(a) for a, _ in rows]); ys = np.array([float(b) for _, b in rows])
    return xs, ys

def dado(cid):
    rec = record(cid); case = rec.validation_case
    cx, cr = load_full_curve(rec.csv_path.relative_to(repo_root()).as_posix())
    off = float(getattr(case, 'csv_x_offset', 0.0) or 0.0)
    cx = np.maximum(cx - off, 0.0) * float(getattr(case, 'csv_x_scale', 1.0) or 1.0)
    cr = cr / max(cr[0], 1e-9)
    k = cr >= runner.FLOOR_TRIM
    return cx[k], cr[k] / cr[k][0]

def sim_energy(cid, k_E):
    """wear energetico via k_wear_spec(n) = k_E * mu_sched(n); K_archard=0 mata a via legada."""
    rec, case, load, geom, kw, _ = H['build'](cid)
    kw2 = dict(kw); kw2.update(mu_thread=0.05, K_archard=0.0)
    xs_mu, ys_mu = mu_de(TAG[cid])
    mat = JointMaterial(**kw2)
    ana = DynamicStiffnessAnalyzer(geom, mat, case.initial_preload_N)
    d = load['delta_mm'] * 1e-3
    x, rd = dado(cid)
    N = int(x[-1])
    r = np.empty(N + 1); r[0] = 1.0
    for n in range(1, N + 1):
        mu_n = float(np.interp(n, xs_mu, ys_mu))
        mat.k_wear_spec = k_E * mu_n
        ana.step_cycle(load['F_amp_N'], load['theta'], case.frequency_Hz, delta_amp=d)
        ana.history.clear()
        r[n] = max(ana.state.F_0, 0.0) / case.initial_preload_N
    al = max(np.interp(float(x[0]), np.arange(N + 1), r), 1e-9)
    p = np.interp(x, np.arange(N + 1), r / al)
    e = np.abs(p - rd)
    return float(e.mean()), float(e.max())

P = print
P('1) ancora: varredura 1D de k_E no test4 (grade log)')
grade = [1e-15, 3e-15, 1e-14, 3e-14, 1e-13, 3e-13]
melhor = None
for kE in grade:
    m, x_ = sim_energy(ALVOS[0], kE)
    P('   k_E=%.0e -> %.4f/%.4f' % (kE, m, x_))
    if melhor is None or m < melhor[1]:
        melhor = (kE, m, x_)
# refino 3 pontos em torno do melhor
kb = melhor[0]
for kE in [kb / 1.8, kb * 1.8]:
    m, x_ = sim_energy(ALVOS[0], kE)
    P('   k_E=%.0e -> %.4f/%.4f (refino)' % (kE, m, x_))
    if m < melhor[1]:
        melhor = (kE, m, x_)
kE = melhor[0]
P('   ancora: k_E=%.2e  test4 %.4f/%.4f' % melhor)
P('')
P('2) transferencia ZERO-REFIT (cegas):')
res = {ALVOS[0]: [melhor[1], melhor[2]]}
for cid in ALVOS[1:]:
    m, x_ = sim_energy(cid, kE)
    res[cid] = [m, x_]
    s = STORE[cid]
    P('   %-6s store %.3f/%.3f -> %.4f/%.4f %s'
      % (TAG[cid], s['mae'], s['maxerr'], m, x_,
         'P' if (m <= .1 and x_ < .1) else 'F'))
ok4 = res[ALVOS[0]][0] <= .1 and res[ALVOS[0]][1] < .1
n_out = sum(1 for c in ALVOS[1:] if res[c][0] <= .1 and res[c][1] < .1)
P('')
P('regua G-CHU-a: test4 %s, cegas %d/3 => %s'
  % ('PASS' if ok4 else 'FAIL', n_out,
     'SATISFAZIVEL - escrever prereg novo' if (ok4 and n_out >= 2) else 'NAO satisfaz'))
json.dump(dict(k_E=kE, tripe=res), open('New_Theory/chu_energywear_sonda.json', 'w'), indent=1)
P('-> New_Theory/chu_energywear_sonda.json')
