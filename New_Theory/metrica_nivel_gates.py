"""Gates N0-N6 + Bloco B do prereg 2026-07-28-metrica-nivel.

Gates CONGELADOS em 3619af5 (esclarecimentos de implementacao em 2026-07-28,
tambem antes de medir). Nada aqui os altera.

Uso: py -3.12 New_Theory/metrica_nivel_gates.py
"""
import sys, json, pathlib
import numpy as np
sys.path.insert(0, str(pathlib.Path('src').resolve()))
from bolt_analysis_studio.validation import runner
from bolt_analysis_studio.validation.case_registry import record, all_records

STORE = pathlib.Path('Models/CALIBRATION_AND_VALIDATION/validation_store.json')
TRIPE = lambda m, x: (m is not None and x is not None and m <= 0.10 and x < 0.10)
# limiar de LEITURA (nao e' gate): janela de colapso degenerada
DEGEN_DCOL, DEGEN_PTS = 100.0, 3

new = json.loads(STORE.read_text(encoding='utf-8'))
P = print
P('=' * 78)
P('GATES N0-N6 -- metrica por correspondencia de NIVEL (congelados em 3619af5)')
P('=' * 78)
com = {c: v for c, v in new.items() if v.get('knee_n') is not None}
sem = {c: v for c, v in new.items()
       if v.get('knee_n') is None and v.get('mae_lvl') is not None}
P('casos: %d | COM joelho: %d | SEM joelho: %d | sem metrica: %d'
  % (len(new), len(com), len(sem), len(new) - len(com) - len(sem)))

# ----------------------------------------------------------------- N5 / N0
fps = {v.get('engine_fingerprint') for v in new.values()}
n5 = (fps == {'4f5bedfbace4'})
P('')
P('N5 fingerprint inalterado ............ %s %s' % ('OK' if n5 else 'FALHA', fps))

n0_bad = [c for c, v in sem.items()
          if abs(v['mae_lvl'] - v['mae']) > 0 or abs(v['maxerr_lvl'] - v['maxerr']) > 0]
n0 = not n0_bad
P('N0 inercia TOTAL sem joelho .......... %s  (%d curvas; %d divergem)'
  % ('OK (bit-a-bit)' if n0 else 'FALHA', len(sem), len(n0_bad)))

# ----------------------------------------------------------------------- N1
n1_bad, n1_pts = [], 0
for c, v in com.items():
    x = np.asarray(v['metric_x'], float)
    pr = np.asarray(v['metric_pred'], float)
    rd = np.asarray(v['metric_data'], float)
    lv = np.asarray(v.get('metric_lvl') or [], float)
    if len(lv) != len(x):
        n1_bad.append((c, 'sem vetor'))
        continue
    pre = x < float(v['knee_n'])
    n1_pts += int(pre.sum())
    d = np.abs(np.abs(lv[pre]) - np.abs(pr[pre] - rd[pre]))
    if len(d) and d.max() > 1e-12:
        n1_bad.append((c, float(d.max())))
n1 = not n1_bad
P('N1 inercia no PLATO (com joelho) ..... %s  (%d pontos pre-joelho; %d curvas violam)'
  % ('OK' if n1 else 'FALHA', n1_pts, len(n1_bad)))
for t in n1_bad[:5]:
    P('     %s' % (t,))

# ----------------------------------------------------------------- N3 / N4 / N6
viradas, pioras, ja = [], [], 0
for c, v in new.items():
    if v.get('mae') is None or v.get('mae_lvl') is None:
        continue
    a, b = TRIPE(v['mae'], v['maxerr']), TRIPE(v['mae_lvl'], v['maxerr_lvl'])
    if a and not b:
        pioras.append((c, 'PERDE O TRIPE'))
    elif a:
        ja += 1
    elif b:
        viradas.append(c)
    if v['maxerr_lvl'] > v['maxerr'] + 1e-12 and not (a and not b):
        pioras.append((c, 'piora res.max'))
n4 = len(viradas) <= 25
P('')
P('N4 viradas (falha->passe) ............ %d  %s'
  % (len(viradas), 'OK' if n4 else 'ESTOUROU 25 -> PARAR'))

n3_bad = []
for c in viradas:
    v = new[c]
    if v.get('knee_n') is None or (v.get('maxerr_at') or 0) < float(v['knee_n']):
        n3_bad.append(c)
n3 = not n3_bad
P('N3 virada so no colapso .............. %s%s'
  % ('OK' if n3 else 'FALHA', '' if n3 else ' -> ' + ', '.join(n3_bad[:4])))
for c in sorted(viradas):
    v = new[c]
    P('     VIROU %-38s %.4f/%.4f -> %.4f/%.4f  (dcol=%s)'
      % (c, v['mae'], v['maxerr'], v['mae_lvl'], v['maxerr_lvl'],
         ('%.0f' % v['delta_col']) if v.get('delta_col') else '-'))

# N6: existe piora? e ela e' LEGITIMA ou de janela degenerada?
P('')
uniq = sorted({c for c, _ in pioras})
n6 = len(uniq) > 0
degen, legit = [], []
for c in uniq:
    v = new[c]
    dc = v.get('delta_col')
    npts = sum(1 for xx in v['metric_x'] if xx >= float(v['knee_n'])) if v.get('knee_n') else 0
    (degen if (dc is not None and (dc < DEGEN_DCOL or npts < DEGEN_PTS)) else legit).append(c)
P('N6 a metrica NAO e unilateral ........ %s  (%d curvas pioram)'
  % ('OK' if n6 else 'FALHA -> unilateral disfarcada', len(uniq)))
P('     das quais JANELA DEGENERADA (dcol<%.0f ou <%d pts): %d'
  % (DEGEN_DCOL, DEGEN_PTS, len(degen)))
P('     das quais piora LEGITIMA: %d' % len(legit))
P('%-40s %-17s %-17s %9s %s' % ('curva que piora', 'antes', 'depois', 'dcol', 'leitura'))
for c in uniq[:20]:
    v = new[c]
    P('%-40s %-17s %-17s %9s %s'
      % (c, '%.4f/%.4f' % (v['mae'], v['maxerr']),
         '%.4f/%.4f' % (v['mae_lvl'], v['maxerr_lvl']),
         ('%.0f' % v['delta_col']) if v.get('delta_col') else '-',
         'DEGENERADA' if c in degen else 'legitima'))

# ----------------------------------------------------------------------- N2
P('')
P('=' * 78)
P('N2 -- DISCRIMINANCIA no fig2 fino: cliff >= 2x a rampa em res.max E falha?')
P('=' * 78)
src = pathlib.Path('New_Theory/liu2025_ramp_v2_gates.py').read_text(encoding='utf-8')
H = {}
exec(compile(src.split('P = print')[0], 'harness', 'exec'), H)
CID = 'liu2025_M16_fig2_single'
a = np.genfromtxt('New_Theory/liu2025_fig2_fine.csv', delimiter=',', skip_header=1)
xx, rr = a[:, 0], a[:, 1] / a[0, 1]
k = rr >= runner.FLOOR_TRIM
FINE = (xx[k], rr[k] / rr[k][0])
n = H['n_span'](CID)
res = {}
for nome, ramp in (('sem forma', None), ('rampa', (0.75, 8.0, H['NF_PAPER'][CID])),
                   ('CLIFF', (0.999, 1.0, H['NF_PAPER'][CID]))):
    r = H['sim'](CID, n, ramp=ramp)
    x, rd = FINE
    m = x <= n
    x, rd = x[m], rd[m]
    al = max(np.interp(float(x[0]), np.arange(n + 1), r), 1e-9)
    sv, kn, dc = runner.level_residuals(x, rd, np.arange(n + 1), r / al)
    e = np.abs(sv)
    res[nome] = (float(e.mean()), float(e.max()), kn, dc)
    P('  %-10s  mae %.4f  res.max %.4f  %s   (joelho=%s dcol=%s)'
      % (nome, e.mean(), e.max(), 'PASSA' if TRIPE(e.mean(), e.max()) else 'falha',
         ('%.0f' % kn) if kn else '-', ('%.0f' % dc) if dc else '-'))
razao = res['CLIFF'][1] / max(res['rampa'][1], 1e-9)
n2 = razao >= 2.0 and not TRIPE(res['CLIFF'][0], res['CLIFF'][1])
P('  razao cliff/rampa em res.max: %.2fx  (criterio >= 2.00x)' % razao)
P('  PREVISAO do prereg: cliff ~0.306, rampa ~0.110, razao ~2.8x, ambos falham')
P('  N2 %s' % ('OK' if n2 else 'FALHA -> abandonar a linha inteira'))

# -------------------------------------------------------------------- Bloco B
P('')
P('=' * 78)
P('BLOCO B -- as curvas TRIMADAS pontuadas na curva INTEIRA (medicao, nao gate)')
P('=' * 78)
trimadas = []
for rec in all_records():
    try:
        t = runner._trim_n_for(rec.source, rec.case_id, rec.validation_case.bolt_size)
    except Exception:
        t = None
    if t is not None:
        trimadas.append((rec, t))
P('  curvas com trim_n_max: %d' % len(trimadas))
# NAO mexer em _MAX_POINTS: a metrica ja e' computada sobre o array DENSO dentro
# de _simulate_case; subir o limite so incharia cycles/ratio/decomp na saida.
_orig = runner._trim_n_for
runner._trim_n_for = lambda *a, **k: None       # pontua a curva INTEIRA
P('%-40s %-17s %-17s %s' % ('curva (SEM trim)', 'vertical', 'nivel', 'tripe'))
passa_b = 0
linhas = []
for rec, t in trimadas:
    try:
        r = runner.simulate_case(rec)
    except Exception as e:
        P('%-40s ERRO %s' % (rec.case_id, e))
        continue
    ok = TRIPE(r.mae_lvl, r.maxerr_lvl)
    passa_b += int(ok)
    linhas.append(dict(cid=rec.case_id, trim=t, mae=r.mae, maxerr=r.maxerr,
                       mae_lvl=r.mae_lvl, maxerr_lvl=r.maxerr_lvl,
                       knee=r.knee_n, dcol=r.delta_col, passa=ok))
    P('%-40s %-17s %-17s %s'
      % (rec.case_id, '%.4f/%.4f' % (r.mae, r.maxerr),
         '%.4f/%.4f' % (r.mae_lvl, r.maxerr_lvl), 'PASSA' if ok else 'falha'))
runner._trim_n_for = _orig
P('  => sob a metrica de NIVEL e SEM trim, passam %d de %d' % (passa_b, len(trimadas)))

P('')
P('=' * 78)
P('VEREDICTO')
P('=' * 78)
for k_, ok in (('N0', n0), ('N1', n1), ('N2', n2), ('N3', n3), ('N4', n4),
               ('N5', n5), ('N6', n6)):
    P('  %s %s' % (k_, 'OK' if ok else 'FALHA'))
P('')
P('  META (janelas de hoje): %d -> %d de %d'
  % (ja, ja + len(viradas), sum(1 for v in new.values() if v.get('mae_lvl') is not None)))
json.dump({'gates': {'N0': n0, 'N1': n1, 'N2': n2, 'N3': n3, 'N4': n4,
                     'N5': n5, 'N6': n6},
           'viradas': sorted(viradas), 'pioras': uniq, 'degeneradas': degen,
           'pioras_legitimas': legit, 'n2': {k: res[k][:2] for k in res},
           'razao_cliff_rampa': razao, 'bloco_b': linhas, 'bloco_b_passa': passa_b,
           'com_joelho': len(com), 'sem_joelho': len(sem)},
          open('New_Theory/metrica_nivel_result.json', 'w'), indent=1)
P('  -> New_Theory/metrica_nivel_result.json')
