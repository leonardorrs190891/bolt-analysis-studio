"""Gates B0-B6 + Bloco C do prereg 2026-07-28-metrica-banda.

Gates CONGELADOS em 0e97d6a, ANTES da implementacao. Nada aqui os altera.
Uso: py -3.12 New_Theory/metrica_banda_gates.py
"""
import sys, json, pathlib
import numpy as np
sys.path.insert(0, str(pathlib.Path('src').resolve()))
from bolt_analysis_studio.validation import runner
from bolt_analysis_studio.validation.case_registry import all_records

STORE = pathlib.Path('Models/CALIBRATION_AND_VALIDATION/validation_store.json')
TRIPE = lambda m, x: (m is not None and x is not None and m <= 0.10 and x < 0.10)
CANON = ('Models/CALIBRATION_AND_VALIDATION/curve_library/digitized_csv/'
         'liu2025_M16_fig2_single.csv')
FINE = 'New_Theory/liu2025_fig2_fine.csv'

new = json.loads(STORE.read_text(encoding='utf-8'))
P = print
P('=' * 78)
P('GATES B0-B6 -- metrica de BANDA (congelados em 0e97d6a)')
P('=' * 78)
comp = [c for c, v in new.items() if v.get('mae_band') is not None]
P('casos: %d | com metrica de banda: %d' % (len(new), len(comp)))

# ----------------------------------------------------------------- B5 / B4 / B3
fps = {v.get('engine_fingerprint') for v in new.values()}
b5 = (fps == {'4f5bedfbace4'})
P('')
P('B5 fingerprint inalterado ............ %s %s' % ('OK' if b5 else 'FALHA', fps))

viradas, perdas, ja = [], [], 0
for c in comp:
    v = new[c]
    a, b = TRIPE(v['mae'], v['maxerr']), TRIPE(v['mae_band'], v['maxerr_band'])
    if a and b:
        ja += 1
    elif a and not b:
        perdas.append(c)
    elif b:
        viradas.append(c)
b4 = len(viradas) <= 25
P('B4 viradas (falha->passe) ............ %d  %s   [perdas: %d]'
  % (len(viradas), 'OK' if b4 else 'ESTOUROU 25 -> PARAR', len(perdas)))


def largura_no_ponto(v, x0):
    """largura da banda no ponto x0, lida do store (sem re-simular)."""
    x = np.asarray(v.get('metric_x') or [], float)
    lo = np.asarray(v.get('band_lo') or [], float)
    hi = np.asarray(v.get('band_hi') or [], float)
    if len(x) == 0 or len(lo) != len(x) or x0 is None:
        return 0.0
    k = int(np.argmin(np.abs(x - float(x0))))
    return float(hi[k] - lo[k])


b3_bad = []
P('')
P('B3 -- toda virada precisa de banda LARGA (>0.05) no ponto critico antigo')
P('%-40s %-17s %-17s %9s %s' % ('curva que virou', 'antes', 'depois', 'largura', ''))
for c in sorted(viradas):
    v = new[c]
    w = largura_no_ponto(v, v.get('maxerr_at'))
    ok = w > 0.05
    if not ok:
        b3_bad.append(c)
    P('%-40s %-17s %-17s %9.4f %s'
      % (c, '%.4f/%.4f' % (v['mae'], v['maxerr']),
         '%.4f/%.4f' % (v['mae_band'], v['maxerr_band']), w,
         'ok' if ok else 'ESTREITA <<<'))
b3 = not b3_bad
P('  B3 %s%s' % ('OK' if b3 else 'FALHA',
                 '' if b3 else ' -> brecha: ' + ', '.join(b3_bad[:4])))

# ----------------------------------------------------------------------- B2
melhoras = np.array([new[c]['maxerr'] - new[c]['maxerr_band'] for c in comp])
med = float(np.median(melhoras))
b2 = med < 0.005
P('')
P('B2 nao e afrouxamento cego ........... %s  (mediana da melhora em res.max = %.5f; criterio < 0.005)'
  % ('OK' if b2 else 'FALHA -> desconto uniforme', med))
P('     media %.5f  p90 %.5f  max %.5f' % (melhoras.mean(),
                                           float(np.percentile(melhoras, 90)),
                                           melhoras.max()))

# ----------------------------------------------------------------------- B6
planas, b6_bad = 0, []
for c in comp:
    v = new[c]
    lo = np.asarray(v.get('band_lo') or [], float)
    hi = np.asarray(v.get('band_hi') or [], float)
    if len(lo) == 0:
        continue
    if float((hi - lo).max()) >= 0.02:
        continue
    planas += 1
    if abs(v['maxerr'] - v['maxerr_band']) > 0.005:
        b6_bad.append((c, v['maxerr'] - v['maxerr_band']))
b6 = not b6_bad
P('')
P('B6 inercia em curva PLANA (<=0.005) .. %s  (%d curvas planas; %d violam)'
  % ('OK' if b6 else 'FALHA', planas, len(b6_bad)))
for c, d in sorted(b6_bad, key=lambda t: -abs(t[1]))[:6]:
    P('     %-40s delta %.4f' % (c, d))

# ------------------------------------------------------------------ B0 / B1
P('')
P('=' * 78)
P('B0 (invariancia a amostragem) + B1 (discriminancia) no fig2, 2 digitalizacoes')
P('=' * 78)
src = pathlib.Path('New_Theory/liu2025_ramp_v2_gates.py').read_text(encoding='utf-8')
H = {}
exec(compile(src.split('P = print')[0], 'harness', 'exec'), H)
CID = 'liu2025_M16_fig2_single'
NF = H['NF_PAPER'][CID]


def load(p):
    a = np.genfromtxt(p, delimiter=',', skip_header=1)
    x, r = a[:, 0], a[:, 1] / a[0, 1]
    k = r >= runner.FLOOR_TRIM
    return x[k], r[k] / r[k][0]


tab = {}
for nome, path in (('canonica 15pt', CANON), ('fina 124pt', FINE)):
    x, rd = load(path)
    n = int(max(x[-1], NF))
    mx = np.arange(n + 1)
    linha = {}
    for f, ramp in (('sem forma', None), ('rampa', (0.75, 8.0, NF)),
                    ('CLIFF', (0.999, 1.0, NF))):
        r = H['sim'](CID, n, ramp=ramp)
        al = max(np.interp(float(x[0]), mx, r), 1e-9)
        sb, _, _, hn = runner.band_residuals(x, rd, mx, r / al)
        e = np.abs(sb)
        linha[f] = (float(e.mean()), float(e.max()), TRIPE(e.mean(), e.max()))
    tab[nome] = linha
    P('  %-14s h_N=%-7.0f %s' % (nome, hn, '  '.join(
        '%s %.4f/%.4f %s' % (f, linha[f][0], linha[f][1], 'P' if linha[f][2] else 'F')
        for f in ('sem forma', 'rampa', 'CLIFF'))))

ver_ok = all(tab['canonica 15pt'][f][2] == tab['fina 124pt'][f][2]
             for f in ('sem forma', 'rampa', 'CLIFF'))
r1, r2 = tab['canonica 15pt']['rampa'][1], tab['fina 124pt']['rampa'][1]
dif = abs(r1 - r2) / max(r1, r2)
b0 = ver_ok and dif <= 0.20
P('  veredictos identicos: %s | res.max da rampa %.4f vs %.4f = %.1f%% (criterio <=20%%)'
  % (ver_ok, r1, r2, 100 * dif))
P('  PREVISAO do prereg: F/P/F nas duas; 0.0521 vs 0.0542 = 4.0%%')
P('  B0 %s' % ('OK' if b0 else 'FALHA -> a banda herda a amostragem'))

b1 = all(tab[k]['rampa'][2] and not tab[k]['CLIFF'][2] and not tab[k]['sem forma'][2]
         for k in tab)
P('  B1 %s  (rampa passa nas duas; cliff e sem-forma falham nas duas)'
  % ('OK' if b1 else 'FALHA -> 3a morte pela mesma causa; a linha fecha'))

# -------------------------------------------------------------------- Bloco C
P('')
P('=' * 78)
P('BLOCO C -- as 16 curvas TRIMADAS pontuadas INTEIRAS sob a banda (medicao)')
P('=' * 78)
trimadas = []
for rec in all_records():
    try:
        t = runner._trim_n_for(rec.source, rec.case_id, rec.validation_case.bolt_size)
    except Exception:
        t = None
    if t is not None:
        trimadas.append(rec)
_orig = runner._trim_n_for
runner._trim_n_for = lambda *a, **k: None
passa_c, linhas = 0, []
P('%-42s %-17s %-17s %s' % ('curva (SEM trim)', 'vertical', 'banda', 'tripe'))
for rec in trimadas:
    try:
        r = runner.simulate_case(rec)
    except Exception as e:
        P('%-42s ERRO %s' % (rec.case_id, e))
        continue
    ok = TRIPE(r.mae_band, r.maxerr_band)
    passa_c += int(ok)
    linhas.append(dict(cid=rec.case_id, mae=r.mae, maxerr=r.maxerr,
                       mae_band=r.mae_band, maxerr_band=r.maxerr_band, passa=ok))
    P('%-42s %-17s %-17s %s'
      % (rec.case_id, '%.4f/%.4f' % (r.mae, r.maxerr),
         '%.4f/%.4f' % (r.mae_band, r.maxerr_band), 'PASSA' if ok else 'falha'))
runner._trim_n_for = _orig
P('  => sob a BANDA e SEM trim, passam %d de %d  (sob a metrica de nivel: 0 de 16)'
  % (passa_c, len(trimadas)))

P('')
P('=' * 78)
P('VEREDICTO')
P('=' * 78)
for k_, ok in (('B0', b0), ('B1', b1), ('B2', b2), ('B3', b3), ('B4', b4),
               ('B5', b5), ('B6', b6)):
    P('  %s %s' % (k_, 'OK' if ok else 'FALHA'))
P('')
P('  META (janelas de hoje): %d -> %d de %d' % (ja + len(perdas),
                                                ja + len(viradas), len(comp)))
json.dump({'gates': {'B0': b0, 'B1': b1, 'B2': b2, 'B3': b3, 'B4': b4,
                     'B5': b5, 'B6': b6},
           'viradas': sorted(viradas), 'perdas': sorted(perdas),
           'mediana_melhora': med, 'b0_tab': {k: {f: tab[k][f][:2] for f in tab[k]}
                                              for k in tab},
           'bloco_c': linhas, 'bloco_c_passa': passa_c,
           'antes': ja + len(perdas), 'depois': ja + len(viradas)},
          open('New_Theory/metrica_banda_result.json', 'w'), indent=1)
P('  -> New_Theory/metrica_banda_result.json')
