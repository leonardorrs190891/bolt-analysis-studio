"""Execucao dos gates do PREREG v2 (specs/2026-07-28-liu2025-fracture-ramp-prereg-v2).

Gates CONGELADOS no commit 5ce4324, ANTES desta medicao. Nada aqui os altera.

E1: tolerancia em VIDA (ciclo de cruzamento), normalizada pela LARGURA da janela
    de colapso  Delta_col = N_f(paper) - trim_n_max(registrado).
E2: N_f LIDO da matriz de ensaios (isola a FORMA do RELOGIO).
E3: banco de prova = nucleo coerente amp0p4/0p5/0p6.

Engine canonico NAO tocado: a forma entra por loss_mechanisms=[...].
"""
import sys, pathlib, json, time

sys.path.insert(0, str(pathlib.Path('src').resolve()))

import numpy as np

from bolt_analysis_studio.validation import runner
from bolt_analysis_studio.validation.case_registry import record
from bolt_analysis_studio.validation.inputs import (load_full_curve, repo_root,
                                                    geometry_for_case)
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointMaterial, LossMechanism, EmbeddingLoss,
    CreepLoss, WearLoss, RotationalLooseningLoss, ThreadFrettingLoss, k_j_ax)

# ---------------------------------------------------------------- constantes
# N_f DECLARADO na matriz de ensaios do artigo ("cycles to end") -- prereg v2 1.1
NF_PAPER = {'liu2025_M16_amp0p25': 330000.0, 'liu2025_M16_amp0p3': 250000.0,
            'liu2025_M16_amp0p4': 77000.0, 'liu2025_M16_amp0p5': 38000.0,
            'liu2025_M16_amp0p6': 24200.0, 'liu2025_M16_amp0p8': 14400.0,
            'liu2025_M16_fig2_single': 10000.0}
CORE = ['liu2025_M16_amp0p4', 'liu2025_M16_amp0p5', 'liu2025_M16_amp0p6']
NOFRAC = ['liu2025_M16_amp0p25', 'liu2025_M16_amp0p3']          # G2
EXTREMAS = ['liu2025_M16_amp0p25', 'liu2025_M16_amp0p3',
            'liu2025_M16_amp0p8', 'liu2025_M16_fig2_single']    # G5 (nao-gate)
CIDS = list(NF_PAPER)

LEVELS = [0.80, 0.70, 0.60, 0.50, 0.40]                         # prereg v2 §2
D_ON_GRID = [0.70, 0.75, 0.80, 0.85, 0.90]                      # prereg v2 §3
Q_GRID = [1.0, 2.0, 3.0, 5.0, 8.0]
TOL_FRAC = 0.15                                                 # 0,15 * Delta_col
CLIFF = (0.999, 1.0)                                            # G3 (ii)
STORE = pathlib.Path('Models/CALIBRATION_AND_VALIDATION/validation_store.json')


class RampLoss(LossMechanism):
    """B1 do prereg. mat._ramp = (D_on, q, nf); None = forma DESLIGADA."""
    name = "fatigue"

    def rate(self, state, geom, mat, F_amp, theta_load, freq, cycle_N,
             slip_amp_override=None, delta_amp=None):
        cfg = getattr(mat, "_ramp", None)
        if cfg is None or state.F_0 <= 0.0:
            return dict(dF_0=0.0, dE_dissipated=0.0, ds={})
        D_on, q, nf = cfg
        D0 = min(max((cycle_N - 1) / nf, 0.0), 1.0)
        D1 = min(cycle_N / nf, 1.0)
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
                    ds=dict(D_fatigue=D1 - D0))


# ------------------------------------------------------------------- arnes
_c = {}


def build(cid):
    if cid not in _c:
        rec = record(cid)
        case = rec.validation_case
        load = runner._loading_for(rec)
        inp = load['inputs']
        geom = geometry_for_case(case, grip_mm=inp['grip_mm']['value'],
                                 E=(inp.get('E') or {}).get('value'))
        geom = runner._apply_adopted_geometry(geom, rec.source, rec.case_id,
                                              case.bolt_size)
        kw = runner.material_kwargs_for(rec, inp)
        trim = runner._trim_n_for(rec.source, rec.case_id, case.bolt_size)
        # paridade com o runner: se houvesse espectro de amplitude, este arnes
        # (delta constante) NAO reproduziria o canonico. Falha alto, nao calado.
        consts, _ = runner.frozen_constants()
        ov = runner._effective_overrides(rec, consts)
        assert 'delta_spectrum' not in ov, (cid, 'delta_spectrum: arnes invalido')
        _c[cid] = (rec, case, load, geom, kw, trim)
    return _c[cid]


def sim(cid, n_max, ramp=None):
    rec, case, load, geom, kw, trim = build(cid)
    mat = JointMaterial(**kw)
    object.__setattr__(mat, '_ramp', ramp)
    ana = DynamicStiffnessAnalyzer(
        geom, mat, case.initial_preload_N,
        loss_mechanisms=[EmbeddingLoss(), CreepLoss(), WearLoss(),
                         RotationalLooseningLoss(), ThreadFrettingLoss(),
                         RampLoss()])
    d = load['delta_mm'] * 1e-3 if load['mode'] == 'displacement' else None
    F0 = case.initial_preload_N
    r = np.empty(n_max + 1)
    r[0] = 1.0
    for n in range(1, n_max + 1):
        ana.step_cycle(load['F_amp_N'], load['theta'], case.frequency_Hz,
                       delta_amp=d)
        r[n] = max(ana.state.F_0, 0.0) / F0
    return r


# dado de gate: mesma convencao do runner (FLOOR_TRIM + normaliza no 1o ponto)
DATA, TRIM = {}, {}
for cid in CIDS:
    rec = record(cid)
    cx, cr = load_full_curve(rec.csv_path.relative_to(repo_root()).as_posix())
    cr = cr / cr[0]
    k = cr >= runner.FLOOR_TRIM
    cx, cr = cx[k], cr[k]
    DATA[cid] = (cx, cr / cr[0])
    TRIM[cid] = build(cid)[5]


def aligned(r, cid):
    """modelo alinhado no 1o ciclo do dado -- identico a CaseResult.align."""
    cx, _ = DATA[cid]
    n = len(r) - 1
    al = max(np.interp(float(cx[0]), np.arange(n + 1), r), 1e-9)
    return r / al


def met(r, cid, trim=None):
    """MAE/maxerr/sigma na convencao canonica (opcionalmente pos-trim)."""
    cx, cr = DATA[cid]
    n = len(r) - 1
    m = cx <= n
    if trim is not None:
        m &= (cx <= trim)
    cd, rd = cx[m], cr[m]
    p = np.interp(cd, np.arange(n + 1), aligned(r, cid))
    s = p - rd
    e = np.abs(s)
    return float(e.mean()), float(e.max()), float(np.std(s))


def crossing(x, y, lvl):
    """1o N em que a curva DESCE a y <= lvl (interp linear). None = nunca."""
    for i in range(1, len(y)):
        if y[i] <= lvl < y[i - 1]:
            t = (y[i - 1] - lvl) / max(y[i - 1] - y[i], 1e-12)
            return float(x[i - 1] + t * (x[i] - x[i - 1]))
    return None


def n_span(cid):
    """simular a VIDA INTEIRA: com relogio lido o modelo colapsa ate N_f, que
    pode passar do ultimo ponto do dado. Simular so ate o dado transformaria
    cruzamento legitimo em 'nunca cruza' -- artefato, nao resultado."""
    return int(max(DATA[cid][0][-1], NF_PAPER[cid]))


def tol(cid):
    return TOL_FRAC * (NF_PAPER[cid] - TRIM[cid])


P = print
P('=' * 78)
P('PREREG v2 -- gates congelados em 5ce4324. Execucao %s' % time.strftime('%Y-%m-%d %H:%M'))
P('=' * 78)
P('%-24s %9s %9s %9s %10s %8s' % ('caso', 'N_f', 'trim', 'Delta_col', 'tol[cic]', 'N_sim'))
for cid in CIDS:
    P('%-24s %9.0f %9s %9.0f %10.0f %8d'
      % (cid, NF_PAPER[cid], ('%.0f' % TRIM[cid]) if TRIM[cid] else '-',
         NF_PAPER[cid] - (TRIM[cid] or 0), tol(cid), n_span(cid)))

# INFORMACIONAL (nao e' gate; nao altera nenhum criterio congelado):
# a tolerancia em vida vs a incerteza do PROPRIO dado (+-3% em N, declarada nas
# notas de aparato). No gate VERTICAL do v1 essa razao era 1.2x a 9x -- gate
# afogado no ruido. Aqui mede-se quanta margem sobre a resolucao do dado existe.
P('')
P('INFORMACIONAL -- margem do gate sobre a incerteza do proprio dado')
P('%-24s %10s %10s %8s %s' % ('caso', 'tol[cic]', '+-3% N', 'razao', 'leitura'))
for cid in CORE:
    u = 0.03 * NF_PAPER[cid]
    P('%-24s %10.0f %10.0f %8.2f %s'
      % (cid, tol(cid), u, u / tol(cid),
         'gate ACIMA da resolucao' if u < tol(cid) else 'gate ABAIXO da resolucao'))
P('  n_pts do dado NO COLAPSO (apos o joelho): %s'
  % ', '.join('%s=%d' % (c.split('M16_')[1],
                         int((DATA[c][0] > (TRIM[c] or 0)).sum())) for c in CORE))

# --------------------------------------------------------------------- G0
P('')
P('=' * 78)
P('G0 -- INERCIA: forma desligada reproduz o store 4f5bedfbace4?')
P('=' * 78)
store = json.loads(STORE.read_text(encoding='utf-8'))
BASE = {}
g0_ok = True
P('%-24s %-22s %-22s %s' % ('caso', 'store (mae/max/sig)', 'inline (mae/max/sig)', 'delta_mae'))
for cid in CORE:                      # prereg v2 G0: as 3 do NUCLEO
    r0 = sim(cid, n_span(cid), ramp=None)
    BASE[cid] = r0
    m = met(r0, cid, trim=TRIM[cid])
    s = store[cid]
    ss = (s.get('mae'), s.get('maxerr'), s.get('resid_std'))
    d = abs(m[0] - (ss[0] or 0.0))
    g0_ok &= d < 1e-9
    P('%-24s %-22s %-22s %.2e' % (cid, '%.4f/%.4f/%.4f' % ss,
                                  '%.4f/%.4f/%.4f' % m, d))
P('  => G0 %s' % ('OK (bit-a-bit)' if g0_ok else
                  'DELTA != 0 -- ver leitura L1 (replica inline vs harness) no fim'))

# --------------------------------------------------------------------- G1
P('')
P('=' * 78)
P('G1 -- FORMA EM VIDA no nucleo (%d celulas x 15 cruzamentos)'
  % (len(D_ON_GRID) * len(Q_GRID)))
P('=' * 78)
DX = {cid: {lvl: crossing(*DATA[cid], lvl) for lvl in LEVELS} for cid in CIDS}
P('cruzamentos do DADO (ciclo em que r desce a cada nivel):')
P('%-24s %s' % ('caso', ' '.join('%9s' % ('r=%.2f' % l) for l in LEVELS)))
for cid in CORE:
    P('%-24s %s' % (cid, ' '.join(
        '%9s' % (('%.0f' % DX[cid][l]) if DX[cid][l] else '--') for l in LEVELS)))

results = {}
best = None
P('')
P('%-11s %s %s' % ('celula', ' '.join('%-17s' % c.split('M16_')[1] for c in CORE),
                   '  PASSA'))
for D_on in D_ON_GRID:
    for q in Q_GRID:
        cell, npass, worst = {}, 0, 0.0
        for cid in CORE:
            r = sim(cid, n_span(cid), ramp=(D_on, q, NF_PAPER[cid]))
            ya = aligned(r, cid)
            xs = np.arange(len(r))
            t = tol(cid)
            per = {}
            for lvl in LEVELS:
                nd = DX[cid][lvl]
                if nd is None:
                    continue
                nm = crossing(xs, ya, lvl)
                if nm is None:
                    per[lvl] = (None, float('inf'), False)
                    worst = float('inf')
                    continue
                err = abs(nm - nd)
                ok = err <= t
                npass += int(ok)
                worst = max(worst, err / t)
                per[lvl] = (nm, err, ok)
            cell[cid] = (per, met(r, cid, trim=TRIM[cid]), met(r, cid))
        results[(D_on, q)] = cell
        tag = '%d/15' % npass
        if best is None or npass > best[0] or (npass == best[0] and worst < best[1]):
            best = (npass, worst, D_on, q)
        P('%-11s %s   %s%s'
          % ('D=%.2f q=%.0f' % (D_on, q),
             ' '.join('%-17s' % (''.join('.X'[cell[c][0][l][2]] for l in LEVELS
                                         if l in cell[c][0])) for c in CORE),
             tag, '  <== 15/15' if npass == 15 else ''))

npass, worst, D_on, q = best
P('')
P('  melhor celula: D_on=%.2f q=%.0f  ->  %d/15  (pior erro = %.2fx a tolerancia)'
  % (D_on, q, npass, worst))
P('  G1 %s' % ('PASSA' if npass == 15 else
               ('FALHA PARCIAL (>=12/15)' if npass >= 12 else 'FALHA (<12/15)')))
P('')
P('  detalhe da melhor celula (erro de cruzamento em ciclos / tolerancia):')
P('%-24s %s' % ('caso', ' '.join('%13s' % ('r=%.2f' % l) for l in LEVELS)))
for cid in CORE:
    per = results[(D_on, q)][cid][0]
    P('%-24s %s  (tol %.0f)' % (cid, ' '.join(
        '%13s' % (('%+.0f %s' % (per[l][1], 'ok' if per[l][2] else 'XX'))
                  if l in per and per[l][0] is not None else '--')
        for l in LEVELS), tol(cid)))

# -------------------------------------------------------------------- G1b
P('')
P('=' * 78)
P('G1b -- o PLATO nao regride (N <= trim_n_max, metrica vertical bem-posta)')
P('=' * 78)
g1b_ok = True
P('%-24s %-18s %-18s %s' % ('caso', 'store', 'com rampa', 'delta mae/max'))
for cid in CORE:
    s = store[cid]
    m = results[(D_on, q)][cid][1]
    dm, dx = m[0] - s['mae'], m[1] - s['maxerr']
    ok = dm <= 0.01 and dx <= 0.01
    g1b_ok &= ok
    P('%-24s %-18s %-18s %+.4f/%+.4f %s'
      % (cid, '%.4f/%.4f' % (s['mae'], s['maxerr']), '%.4f/%.4f' % (m[0], m[1]),
         dm, dx, 'ok' if ok else 'XX'))
P('  => G1b %s' % ('PASSA' if g1b_ok else 'FALHA'))

# --------------------------------------------------------------------- G2
P('')
P('=' * 78)
P('G2 -- nao regride quem NAO fratura no range (metrica canonica POS-TRIM)')
P('=' * 78)
g2_ok = True
for cid in NOFRAC:
    r = sim(cid, n_span(cid), ramp=(D_on, q, NF_PAPER[cid]))
    s = store[cid]
    mt = met(r, cid, trim=TRIM[cid])
    mu_ = met(r, cid)                      # informacional (curva inteira)
    dm = mt[0] - s['mae']
    ok = dm <= 0.01
    g2_ok &= ok
    P('  %-24s pos-trim %.4f (store %.4f, %+0.4f) %s | INFORMACIONAL inteira %.3f/%.3f'
      % (cid, mt[0], s['mae'], dm, 'ok' if ok else 'XX', mu_[0], mu_[1]))
P('  => G2 %s' % ('PASSA' if g2_ok else 'FALHA'))

# --------------------------------------------------------------------- G3
P('')
P('=' * 78)
P('G3 -- DISCRIMINANCIA: a rampa passa onde (i) sem forma e (ii) cliff falham?')
P('=' * 78)
alt = {}
for nome, ramp_of in (('sem forma', lambda c: None),
                      ('cliff', lambda c: (CLIFF[0], CLIFF[1], NF_PAPER[c]))):
    tot = 0
    det = []
    for cid in CORE:
        r = BASE[cid] if nome == 'sem forma' else sim(cid, n_span(cid), ramp_of(cid))
        ya = aligned(r, cid)
        xs = np.arange(len(r))
        t = tol(cid)
        marks = ''
        for lvl in LEVELS:
            nd = DX[cid][lvl]
            if nd is None:
                continue
            nm = crossing(xs, ya, lvl)
            ok = nm is not None and abs(nm - nd) <= t
            tot += int(ok)
            marks += '.X'[ok]
        det.append('%-17s' % marks)
    alt[nome] = tot
    P('  %-10s %s  %d/15' % (nome, ' '.join(det), tot))
P('  rampa     %s  %d/15' % (' '.join('%-17s' % ''.join(
    '.X'[results[(D_on, q)][c][0][l][2]] for l in LEVELS
    if l in results[(D_on, q)][c][0]) for c in CORE), npass))
g3_ok = npass == 15 and alt['sem forma'] < 15 and alt['cliff'] < 15
P('  => G3 %s%s' % ('PASSA (a rampa ganha os 2 parametros)' if g3_ok else 'FALHA',
                    '' if npass == 15 else ' -- G1 nao passou; G3 so vale com G1'))

# ------------------------------------------------------------------ G4/G5
P('')
P('=' * 78)
P('G4 -- a perda de secao atravessa o loose_arrest_floor = 0.25?')
P('=' * 78)
for cid in CORE + ['liu2025_M16_fig2_single']:
    r = sim(cid, n_span(cid), ramp=(D_on, q, NF_PAPER[cid]))
    P('  %-24s r_fim: sem rampa %.3f | com rampa %.3f'
      % (cid, (BASE.get(cid) if cid in BASE else sim(cid, n_span(cid)))[-1], r[-1]))

P('')
P('=' * 78)
P('G5 -- extremas com o par vencedor (MEDIDAS, NAO gateadas)')
P('=' * 78)
P('%-24s %-16s %-16s %s' % ('caso', 'pos-trim', 'inteira', 'cruzamentos'))
for cid in EXTREMAS:
    r = sim(cid, n_span(cid), ramp=(D_on, q, NF_PAPER[cid]))
    ya, xs, t = aligned(r, cid), np.arange(len(r)), tol(cid)
    marks = ''.join('.X'[(crossing(xs, ya, l) is not None
                          and DX[cid][l] is not None
                          and abs(crossing(xs, ya, l) - DX[cid][l]) <= t)]
                    for l in LEVELS if DX[cid][l] is not None)
    P('%-24s %-16s %-16s %s' % (cid, '%.4f/%.4f' % met(r, cid, TRIM[cid])[:2],
                                '%.4f/%.4f' % met(r, cid)[:2], marks or '(nenhum nivel)'))

P('')
P('=' * 78)
P('VEREDICTO (ramos pre-declarados no prereg v2 4.1)')
P('=' * 78)
P('  G0 %s | G1 %d/15 %s | G1b %s | G2 %s | G3 %s'
  % ('OK' if g0_ok else 'DELTA', npass, 'OK' if npass == 15 else 'FALHA',
     'OK' if g1b_ok else 'FALHA', 'OK' if g2_ok else 'FALHA',
     'OK' if g3_ok else 'FALHA'))
json.dump({'best': {'D_on': D_on, 'q': q, 'pass': npass},
           'alt': alt, 'g0': bool(g0_ok), 'g1b': bool(g1b_ok),
           'g2': bool(g2_ok), 'g3': bool(g3_ok),
           'tol': {c: tol(c) for c in CIDS},
           'data_crossings': {c: DX[c] for c in CIDS}},
          open('New_Theory/liu2025_ramp_v2_result.json', 'w'), indent=1)
P('  -> New_Theory/liu2025_ramp_v2_result.json')
