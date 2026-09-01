"""Gates M0-M6 do prereg 2026-07-28 (metrica em vida no trecho vertical).

>>> NAO RODA COMO ESTA. A metrica foi REJEITADA (M2 e M3 falharam) e a
>>> implementacao no runner foi REVERTIDA, entao os campos que este arnes le
>>> (mae_life / maxerr_life / metric_life / runner.life_residuals) nao existem
>>> mais. O arquivo fica como REGISTRO do que foi executado.
>>>   - saida verbatim da varredura ....... New_Theory/metrica_vida_output.txt
>>>   - veredicto e diagnostico ........... New_Theory/metrica_vida_results.md
>>>   - gate DECISIVO (M2), reproduzivel em ~2 min e SEM patch:
>>>         py -3.12 New_Theory/metrica_vida_rejeitada.py

Gates CONGELADOS em 3a26b4a, ANTES da implementacao. Nada aqui os altera.
Le o store re-simulado (campos metric_life/mae_life/... convivendo com os
verticais) e o backup do store ANTES, para medir o delta por curva.

Uso:  py -3.12 New_Theory/metrica_vida_gates.py [store_antes.json]
"""
import sys, json, pathlib
import numpy as np
sys.path.insert(0, str(pathlib.Path('src').resolve()))
from bolt_analysis_studio.validation import runner

STORE = pathlib.Path('Models/CALIBRATION_AND_VALIDATION/validation_store.json')
ANTES = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else None
SIG_R, SIG_NF = runner.SIGMA_R, runner.SIGMA_N_FRAC
TRIPE = lambda mae, mx: (mae is not None and mx is not None
                         and mae <= 0.10 and mx < 0.10)

new = json.loads(STORE.read_text(encoding='utf-8'))
old = json.loads(ANTES.read_text(encoding='utf-8')) if ANTES and ANTES.exists() else {}

P = print
P('=' * 78)
P('GATES M0-M6 -- metrica em vida (prereg congelado em 3a26b4a)')
P('=' * 78)
P('casos no store: %d   com metrica de curva: %d   com campo de vida: %d'
  % (len(new), sum(1 for v in new.values() if v.get('mae') is not None),
     sum(1 for v in new.values() if v.get('mae_life') is not None)))


def slope_at(v, x0):
    """|dr/dN| local do DADO no ponto x0, dos vetores da propria metrica."""
    x = np.asarray(v.get('metric_x') or [], float)
    r = np.asarray(v.get('metric_data') or [], float)
    if len(x) < 2 or x0 is None:
        return 0.0
    g = np.abs(np.gradient(r, x))
    return float(np.interp(x0, x, g))


# ------------------------------------------------------------------ M5 / M6
fps = {v.get('engine_fingerprint') for v in new.values()}
m5 = (fps == {'4f5bedfbace4'})
P('')
P('M5 fingerprint inalterado ...... %s  (%s)' % ('OK' if m5 else 'FALHA', fps))

piora, comparaveis = [], []
for cid, v in new.items():
    if v.get('mae') is None or v.get('mae_life') is None:
        continue
    comparaveis.append(cid)
    if v['mae_life'] > v['mae'] + 1e-12 or v['maxerr_life'] > v['maxerr'] + 1e-12:
        piora.append(cid)
m6 = not piora
P('M6 nenhuma curva piora ......... %s  (%d curvas comparadas%s)'
  % ('OK' if m6 else 'FALHA', len(comparaveis),
     '' if m6 else '; PIORAM: ' + ', '.join(piora[:5])))

# ----------------------------------------------------------------------- M0
# identidade onde a fuga horizontal e' desprezivel: |dr/dN|*sig_N <= 0.1*sig_r
P('')
pior_m0, n_m0 = 0.0, 0
for cid, v in new.items():
    x = np.asarray(v.get('metric_x') or [], float)
    rd = np.asarray(v.get('metric_data') or [], float)
    pr = np.asarray(v.get('metric_pred') or [], float)
    lf = np.asarray(v.get('metric_life') or [], float)
    if len(x) < 2 or len(lf) != len(x):
        continue
    g = np.abs(np.gradient(rd, x))
    plano = g * (SIG_NF * np.abs(x)) <= 0.1 * SIG_R
    if not plano.any():
        continue
    d = np.abs(np.abs(lf[plano]) - np.abs(pr[plano] - rd[plano]))
    n_m0 += int(plano.sum())
    pior_m0 = max(pior_m0, float(d.max()))
m0 = pior_m0 <= 1e-6
P('M0 identidade no trecho plano .. %s  (pior desvio %.2e em %d pontos; limiar 1e-6)'
  % ('OK' if m0 else 'FALHA', pior_m0, n_m0))

# ----------------------------------------------------------------------- M1
# curvas planas (max |dr/dN|*sig_N < 0.2*sig_r) nao podem mudar > 0.001
P('')
m1_viol = []
n_planas = 0
for cid, v in new.items():
    x = np.asarray(v.get('metric_x') or [], float)
    rd = np.asarray(v.get('metric_data') or [], float)
    if len(x) < 2 or v.get('mae_life') is None:
        continue
    g = np.abs(np.gradient(rd, x))
    if (g * (SIG_NF * np.abs(x))).max() >= 0.2 * SIG_R:
        continue
    n_planas += 1
    dm, dx = abs(v['mae_life'] - v['mae']), abs(v['maxerr_life'] - v['maxerr'])
    if dm > 0.001 or dx > 0.001:
        m1_viol.append((cid, dm, dx))
m1 = not m1_viol
P('M1 curva plana nao se mexe ..... %s  (%d curvas planas; %d violam)'
  % ('OK' if m1 else 'FALHA', n_planas, len(m1_viol)))
for cid, dm, dx in sorted(m1_viol, key=lambda t: -t[2])[:8]:
    P('     %-34s dMAE %+.4f  dmax %+.4f' % (cid, -dm, -dx))

# ----------------------------------------------------------------- M4 / M3
P('')
P('=' * 78)
P('M4 -- VIRADAS (falha -> passe) e M3 -- toda virada em trecho INGREME?')
P('=' * 78)
viradas, ja_passavam, seguem_falhando = [], 0, 0
for cid, v in new.items():
    if v.get('mae') is None or v.get('mae_life') is None:
        continue
    antes = TRIPE(v['mae'], v['maxerr'])
    depois = TRIPE(v['mae_life'], v['maxerr_life'])
    if antes:
        ja_passavam += 1
    elif depois:
        viradas.append(cid)
    else:
        seguem_falhando += 1
P('  passavam antes: %d   VIRAM: %d   seguem falhando: %d'
  % (ja_passavam, len(viradas), seguem_falhando))
m4 = len(viradas) <= 25
P('  M4 teto de 25 viradas ........ %s' % ('OK' if m4 else 'ESTOURADO -> PARAR'))

P('')
P('%-34s %-17s %-17s %9s %s' % ('curva que virou', 'antes mae/max',
                                'depois mae/max', 'incl*sigN', 'M3'))
m3_viol = []
for cid in sorted(viradas):
    v = new[cid]
    sl = slope_at(v, v.get('maxerr_at'))
    esc = sl * SIG_NF * abs(float(v.get('maxerr_at') or 0.0))
    ok3 = esc > SIG_R
    if not ok3:
        m3_viol.append(cid)
    P('%-34s %-17s %-17s %9.4f %s'
      % (cid, '%.4f/%.4f' % (v['mae'], v['maxerr']),
         '%.4f/%.4f' % (v['mae_life'], v['maxerr_life']), esc,
         'ingreme' if ok3 else 'RASO <<<'))
m3 = not m3_viol
P('  M3 toda virada em trecho ingreme ... %s%s'
  % ('OK' if m3 else 'FALHA', '' if m3 else ' -> BRECHA: ' + ', '.join(m3_viol)))

# ----------------------------------------------------------------------- M2
P('')
P('=' * 78)
P('M2 -- DISCRIMINANCIA: sem forma e cliff CONTINUAM falhando sob a metrica nova?')
P('=' * 78)
P('  (roda o arnes do prereg v2 com a metrica em vida nas 3 do nucleo + fig2 fino)')
src = pathlib.Path('New_Theory/liu2025_ramp_v2_gates.py').read_text(encoding='utf-8')
H = {}
exec(compile(src.split('P = print')[0], 'harness', 'exec'), H)
CORE = H['CORE'] + ['liu2025_M16_fig2_single']
WIN = (0.75, 8.0)


def met_life(cid, ramp, ref=None):
    n = H['n_span'](cid)
    r = H['sim'](cid, n, ramp=ramp)
    x, rd = ref if ref is not None else H['DATA'][cid]
    m = x <= n
    x, rd = x[m], rd[m]
    al = max(np.interp(float(x[0]), np.arange(n + 1), r), 1e-9)
    sl = runner.life_residuals(x, rd, np.arange(n + 1), r / al)
    e = np.abs(sl)
    return float(e.mean()), float(e.max())


FINE = None
p = pathlib.Path('New_Theory/liu2025_fig2_fine.csv')
if p.exists():
    a = np.genfromtxt(p, delimiter=',', skip_header=1)
    xx, rr = a[:, 0], a[:, 1] / a[0, 1]
    k = rr >= runner.FLOOR_TRIM
    FINE = (xx[k], rr[k] / rr[k][0])

P('%-26s %-18s %-18s %-18s' % ('curva', 'sem forma', 'rampa', 'cliff'))
m2_ok = True
for cid in CORE:
    ref = FINE if (cid.endswith('fig2_single') and FINE is not None) else None
    row = {}
    for nome, ramp in (('sem forma', None), ('rampa', (WIN[0], WIN[1], H['NF_PAPER'][cid])),
                       ('cliff', (0.999, 1.0, H['NF_PAPER'][cid]))):
        row[nome] = met_life(cid, ramp, ref)
    P('%-26s %-18s %-18s %-18s'
      % (cid.split('M16_')[1] + ('(fino)' if ref is not None else ''),
         '%.3f/%.3f %s' % (*row['sem forma'], 'P' if TRIPE(*row['sem forma']) else 'F'),
         '%.3f/%.3f %s' % (*row['rampa'], 'P' if TRIPE(*row['rampa']) else 'F'),
         '%.3f/%.3f %s' % (*row['cliff'], 'P' if TRIPE(*row['cliff']) else 'F')))
    if TRIPE(*row['cliff']) or TRIPE(*row['sem forma']):
        m2_ok = False
P('  M2 discriminancia preservada ....... %s' % ('OK' if m2_ok else 'FALHA -> a metrica virou BRECHA'))

# ------------------------------------------------------------------ resumo
P('')
P('=' * 78)
P('VEREDICTO')
P('=' * 78)
for k, ok in (('M0', m0), ('M1', m1), ('M2', m2_ok), ('M3', m3),
              ('M4', m4), ('M5', m5), ('M6', m6)):
    P('  %s %s' % (k, 'OK' if ok else 'FALHA'))
P('')
P('  META: %d -> %d de %d curvas comparaveis no tripe'
  % (ja_passavam, ja_passavam + len(viradas), len(comparaveis)))
json.dump({'viradas': sorted(viradas), 'm0_pior': pior_m0, 'm1_viol': m1_viol,
           'm3_viol': m3_viol, 'gates': {'M0': m0, 'M1': m1, 'M2': m2_ok,
                                         'M3': m3, 'M4': m4, 'M5': m5, 'M6': m6},
           'antes': ja_passavam, 'depois': ja_passavam + len(viradas),
           'comparaveis': len(comparaveis)},
          open('New_Theory/metrica_vida_result.json', 'w'), indent=1)
P('  -> New_Theory/metrica_vida_result.json')
