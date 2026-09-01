"""Gates C0-C9 + Bloco D do prereg 2026-07-28-metrica-banda-v2 (4a tentativa).

Gates CONGELADOS em af711b8, ANTES da implementacao. Nada aqui os altera.

POS-PROCESSAMENTO PURO: a banda precisa do modelo so nos ciclos do dado, que e'
o vetor `metric_pred` do store. Nenhuma linha de src/ e' tocada e nao ha
re-simulacao (so o Bloco D e o gate cego C4, que simulam curvas SEM trim).

Uso: py -3.12 New_Theory/metrica_banda_v2_gates.py
"""
import sys, json, pathlib, subprocess
import numpy as np
sys.path.insert(0, str(pathlib.Path('src').resolve()))
from bolt_analysis_studio.validation import runner
from bolt_analysis_studio.validation.case_registry import all_records

STORE = pathlib.Path('Models/CALIBRATION_AND_VALIDATION/validation_store.json')
FRAC_N = 0.03
NGRID = 64
TRIPE = lambda m, x: (m is not None and x is not None and m <= 0.10 and x < 0.10)
CANON = ('Models/CALIBRATION_AND_VALIDATION/curve_library/digitized_csv/'
         'liu2025_M16_fig2_single.csv')
FINE = 'New_Theory/liu2025_fig2_fine.csv'


def band_v4b(cd, rd, pred, frac_n=FRAC_N, ngrid=NGRID):
    """Banda v4b (prereg §1): exige EVIDENCIA MEDIDA.

    |S_i| < 2  -> banda [r_i, r_i] => residuo = |dr| EXATO (metrica de hoje)
    |S_i| >= 2 -> banda = [min,max] do dado INTERPOLADO na janela +-h_N
    Devolve (residuo assinado, largura, mascara de 'sem vizinho').
    """
    cd = np.asarray(cd, float)
    rd = np.asarray(rd, float)
    pred = np.asarray(pred, float)
    h = frac_n * float(cd[-1])
    out = np.zeros(len(cd))
    wid = np.zeros(len(cd))
    solo = np.zeros(len(cd), bool)
    for i in range(len(cd)):
        m = np.abs(cd - cd[i]) <= h
        if int(m.sum()) < 2:
            lo = hi = float(rd[i])
            solo[i] = True
        else:
            a, b = max(cd[i] - h, cd[0]), min(cd[i] + h, cd[-1])
            v = np.interp(np.linspace(a, b, ngrid), cd, rd)
            lo, hi = float(v.min()), float(v.max())
        wid[i] = hi - lo
        p = float(pred[i])
        out[i] = (lo - p) if p < lo else ((p - hi) if p > hi else 0.0)
    return out, wid, solo


def agg(cd, rd, pred):
    o, w, s = band_v4b(cd, rd, pred)
    e = np.abs(o)
    k = int(np.argmax(e)) if len(e) else 0
    return (float(e.mean()) if len(e) else None,
            float(e.max()) if len(e) else None, o, w, s, k)


new = json.loads(STORE.read_text(encoding='utf-8'))
P = print
P('=' * 78)
P('GATES C0-C9 -- metrica de BANDA v2 (congelados em af711b8)')
P('=' * 78)

comp = [c for c, v in new.items()
        if v.get('mae') is not None and len(v.get('metric_x') or []) > 1]
P('casos com metrica de curva: %d de %d' % (len(comp), len(new)))

# ------------------------------------------------------------- C9 / C1 / C5 / C7
fps = {v.get('engine_fingerprint') for v in new.values()}
c9 = (fps == {'4f5bedfbace4'})
P('')
P('C9 fingerprint inalterado ............ %s %s' % ('OK' if c9 else 'FALHA', fps))

res = {}
c1_pior, c1_pts = 0.0, 0
c7_bad, melhoras = [], []
for c in comp:
    v = new[c]
    cd = np.asarray(v['metric_x'], float)
    rd = np.asarray(v['metric_data'], float)
    pr = np.asarray(v['metric_pred'], float)
    mae_b, mx_b, o, w, solo, k = agg(cd, rd, pr)
    res[c] = dict(mae=mae_b, maxerr=mx_b, w=w, solo=solo, o=o, cd=cd, rd=rd, pr=pr)
    vert = np.abs(pr - rd)
    if solo.any():                                    # C1
        d = np.abs(np.abs(o[solo]) - vert[solo])
        c1_pior = max(c1_pior, float(d.max()))
        c1_pts += int(solo.sum())
    mud = np.abs(np.abs(o) - vert) > 0.005            # C7
    if len(cd) and mud.mean() >= 0.50:
        c7_bad.append((c, float(mud.mean())))
    melhoras.append(v['maxerr'] - mx_b)

c1 = c1_pior <= 1e-12
P('C1 inercia EXATA sem vizinho medido .. %s  (%d pontos; pior desvio %.2e)'
  % ('OK' if c1 else 'FALHA', c1_pts, c1_pior))

melhoras = np.array(melhoras)
med = float(np.median(melhoras))
c5 = med < 0.005
P('C5 nao e afrouxamento cego ........... %s  (mediana da melhora %.5f; criterio < 0.005)'
  % ('OK' if c5 else 'FALHA', med))
P('     media %.5f  p90 %.5f  max %.5f' % (melhoras.mean(),
                                           float(np.percentile(melhoras, 90)),
                                           melhoras.max()))
c7 = not c7_bad
P('C7 ganho CONCENTRADO (<50%% dos pts) .. %s  (%d curvas violam)'
  % ('OK' if c7 else 'FALHA', len(c7_bad)))
for c, f in sorted(c7_bad, key=lambda t: -t[1])[:6]:
    P('     %-42s %.0f%% dos pontos mudam' % (c, 100 * f))

# --------------------------------------------------------------- C8 / C6
viradas, perdas, ja = [], [], 0
for c in comp:
    v = new[c]
    a, b = TRIPE(v['mae'], v['maxerr']), TRIPE(res[c]['mae'], res[c]['maxerr'])
    if a and b:
        ja += 1
    elif a:
        perdas.append(c)
    elif b:
        viradas.append(c)
c8 = len(viradas) <= 25
P('')
P('C8 viradas (falha->passe) ............ %d  %s   [perdas: %d]'
  % (len(viradas), 'OK' if c8 else 'ESTOUROU 25 -> PARAR', len(perdas)))

c6_bad = []
P('')
P('C6 -- toda virada exige banda LARGA (>0.05) no ponto critico antigo')
if viradas:
    P('%-42s %-17s %-17s %9s %s' % ('curva', 'antes', 'depois', 'largura', ''))
for c in sorted(viradas):
    v, r = new[c], res[c]
    k = int(np.argmax(np.abs(r['pr'] - r['rd'])))
    w = float(r['w'][k])
    ok = w > 0.05
    if not ok:
        c6_bad.append(c)
    P('%-42s %-17s %-17s %9.4f %s'
      % (c, '%.4f/%.4f' % (v['mae'], v['maxerr']),
         '%.4f/%.4f' % (r['mae'], r['maxerr']), w, 'ok' if ok else 'ESTREITA <<<'))
c6 = not c6_bad
P('  C6 %s%s' % ('OK' if c6 else 'FALHA',
                 '' if c6 else ' -> ' + ', '.join(c6_bad[:4])))

# --------------------------------------------------------------- C2 / C3
P('')
P('=' * 78)
P('C2 (invariancia) + C3 (discriminancia no fig2) -- CASO DE PROJETO, ver §0')
P('=' * 78)
src = pathlib.Path('New_Theory/liu2025_ramp_v2_gates.py').read_text(encoding='utf-8')
H = {}
exec(compile(src.split('P = print')[0], 'harness', 'exec'), H)
FIG = 'liu2025_M16_fig2_single'


def load(p):
    a = np.genfromtxt(p, delimiter=',', skip_header=1)
    x, r = a[:, 0], a[:, 1] / a[0, 1]
    k = r >= runner.FLOOR_TRIM
    return x[k], r[k] / r[k][0]


def forma(cid, x, rd, ramp):
    n = int(max(x[-1], H['NF_PAPER'][cid]))
    mx = np.arange(n + 1)
    r = H['sim'](cid, n, ramp=ramp)
    al = max(np.interp(float(x[0]), mx, r), 1e-9)
    pred = np.interp(x, mx, r / al)
    m, xm, *_ = agg(x, rd, pred)
    return m, xm, TRIPE(m, xm)


tabf = {}
for nome, path in (('canonica 15pt', CANON), ('fina 124pt', FINE)):
    x, rd = load(path)
    linha = {}
    for f, ramp in (('sem forma', None), ('rampa', (0.75, 8.0, H['NF_PAPER'][FIG])),
                    ('CLIFF', (0.999, 1.0, H['NF_PAPER'][FIG]))):
        linha[f] = forma(FIG, x, rd, ramp)
    tabf[nome] = linha
    P('  %-14s %s' % (nome, '  '.join('%s %.4f/%.4f %s' % (f, *linha[f][:2],
                                                           'P' if linha[f][2] else 'F')
                                      for f in ('sem forma', 'rampa', 'CLIFF'))))
r1, r2 = tabf['canonica 15pt']['rampa'][1], tabf['fina 124pt']['rampa'][1]
dif = abs(r1 - r2) / max(r1, r2)
ver = all(tabf['canonica 15pt'][f][2] == tabf['fina 124pt'][f][2]
          for f in ('sem forma', 'rampa', 'CLIFF'))
c2 = ver and dif <= 0.20
c3 = all(tabf[k]['rampa'][2] and not tabf[k]['CLIFF'][2]
         and not tabf[k]['sem forma'][2] for k in tabf)
P('  C2 %s (veredictos iguais=%s; res.max rampa %.4f vs %.4f = %.1f%%; previsto 3.7%%)'
  % ('OK' if c2 else 'FALHA', ver, r1, r2, 100 * dif))
P('  C3 %s' % ('OK' if c3 else 'FALHA'))

# ----------------------------------------------------------------------- C4
P('')
P('=' * 78)
P('C4 -- DISCRIMINANCIA CEGA no nucleo amp0p4/0p5/0p6 (conta NAO rodada antes)')
P('=' * 78)
CORE = ['liu2025_M16_amp0p4', 'liu2025_M16_amp0p5', 'liu2025_M16_amp0p6']
n_rampa_ok, n_cliff_ok = 0, 0
P('%-24s %-18s %-18s %-18s' % ('curva (SEM trim)', 'sem forma', 'rampa', 'CLIFF'))
for cid in CORE:
    x, rd = H['DATA'][cid]
    linha = {}
    for f, ramp in (('sem forma', None), ('rampa', (0.75, 8.0, H['NF_PAPER'][cid])),
                    ('CLIFF', (0.999, 1.0, H['NF_PAPER'][cid]))):
        linha[f] = forma(cid, x, rd, ramp)
    n_rampa_ok += int(linha['rampa'][2])
    n_cliff_ok += int(linha['CLIFF'][2])
    P('%-24s %-18s %-18s %-18s' % (cid.split('M16_')[1],
                                   *['%.4f/%.4f %s' % (*linha[f][:2], 'P' if linha[f][2] else 'F')
                                     for f in ('sem forma', 'rampa', 'CLIFF')]))
c4 = (n_rampa_ok >= 2) and (n_cliff_ok == 0)
P('  rampa passa em %d de 3 (criterio >=2) | cliff passa em %d de 3 (criterio 0)'
  % (n_rampa_ok, n_cliff_ok))
P('  C4 %s%s' % ('OK' if c4 else 'FALHA',
                 '' if c4 else ' -> a discriminancia do fig2 era artefato; A LINHA FECHA'))

# -------------------------------------------------------------------- Bloco D
P('')
P('=' * 78)
P('BLOCO D -- as 16 curvas TRIMADAS pontuadas INTEIRAS sob a banda v4b')
P('=' * 78)
trim_recs = []
for rec in all_records():
    try:
        t = runner._trim_n_for(rec.source, rec.case_id, rec.validation_case.bolt_size)
    except Exception:
        t = None
    if t is not None:
        trim_recs.append(rec)
_orig = runner._trim_n_for
runner._trim_n_for = lambda *a, **k: None
passa_d, linhas = 0, []
P('%-42s %-17s %-17s %s' % ('curva (SEM trim)', 'vertical', 'banda v4b', 'tripe'))
for rec in trim_recs:
    try:
        r = runner.simulate_case(rec)
    except Exception as e:
        P('%-42s ERRO %s' % (rec.case_id, e))
        continue
    m, xm, *_ = agg(r.metric_x, r.metric_data, r.metric_pred)
    ok = TRIPE(m, xm)
    passa_d += int(ok)
    linhas.append(dict(cid=rec.case_id, mae=r.mae, maxerr=r.maxerr,
                       mae_band=m, maxerr_band=xm, passa=ok))
    P('%-42s %-17s %-17s %s' % (rec.case_id, '%.4f/%.4f' % (r.mae, r.maxerr),
                                '%.4f/%.4f' % (m, xm), 'PASSA' if ok else 'falha'))
runner._trim_n_for = _orig
P('  => %d de %d  (nivel: 0/16 · banda v1: 10/16)' % (passa_d, len(trim_recs)))

# ----------------------------------------------------------------------- C0
st = subprocess.run(['git', 'status', '--porcelain', 'src/',
                     'Models/CALIBRATION_AND_VALIDATION/validation_store.json'],
                    capture_output=True, text=True).stdout
sujo = [l for l in st.splitlines() if l and not l.startswith('??')]
c0 = not sujo
P('')
P('C0 nada de canonico tocado ........... %s %s' % ('OK' if c0 else 'FALHA', sujo))

P('')
P('=' * 78)
P('VEREDICTO')
P('=' * 78)
for k_, ok in (('C0', c0), ('C1', c1), ('C2', c2), ('C3', c3), ('C4', c4),
               ('C5', c5), ('C6', c6), ('C7', c7), ('C8', c8), ('C9', c9)):
    P('  %s %s' % (k_, 'OK' if ok else 'FALHA'))
P('')
P('  META (janelas de hoje): %d -> %d de %d' % (ja + len(perdas),
                                                ja + len(viradas), len(comp)))
json.dump({'gates': dict(C0=c0, C1=c1, C2=c2, C3=c3, C4=c4, C5=c5, C6=c6,
                         C7=c7, C8=c8, C9=c9),
           'viradas': sorted(viradas), 'perdas': sorted(perdas),
           'mediana_melhora': med, 'c4': dict(rampa_ok=n_rampa_ok, cliff_ok=n_cliff_ok),
           'bloco_d': linhas, 'bloco_d_passa': passa_d,
           'antes': ja + len(perdas), 'depois': ja + len(viradas)},
          open('New_Theory/metrica_banda_v2_result.json', 'w'), indent=1)
P('  -> New_Theory/metrica_banda_v2_result.json')
