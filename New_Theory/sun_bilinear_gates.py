"""Gates S0-S6 do prereg 2026-07-28-sun-bilinear (congelados em 3794090).

Testa o modelo que a FONTE declara: Su-N BILINEAR com fronteira alto/baixo ciclo.
Pos-processamento puro (sigma da Table 2 + N da Fig. 4 digitalizada). Nao toca src/,
nao toca o store, nao adota nada.

Uso: py -3.12 New_Theory/sun_bilinear_gates.py
"""
import json, pathlib, sys
import numpy as np
sys.path.insert(0, str(pathlib.Path('src').resolve()))
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    JointMaterial, sun_life)

# Table 2 do artigo: delta (mm) -> tensao equivalente na raiz (MPa)
T2 = {'M10': {0.3: 391.96, 0.4: 525.05, 0.6: 787.00, 0.8: 988.76},
      'M16': {0.3: 328.70, 0.4: 440.05, 0.6: 660.03, 0.8: 821.65}}
FIG4 = json.load(open('New_Theory/liu2025_fig4_DN.json', encoding='utf-8'))
OUT = pathlib.Path('New_Theory/sun_bilinear_result.json')
P = print


def sigma(bolt, d):
    x = np.array(sorted(T2[bolt]))
    y = np.array([T2[bolt][k] for k in x])
    if d < x[0] or d > x[-1]:
        return float(np.polyval(np.polyfit(x, y, 1), d)), True
    return float(np.interp(d, x, y)), False


DATA = {}
for b in ('M16', 'M10'):
    pts = sorted([(d, N) for N, d in FIG4[b]])
    DATA[b] = [(d, N, *sigma(b, d)) for d, N in pts]


def fit_bilinear(s, n, ngrid=400):
    """LSQ em log-log com joelho varrido e CONTINUIDADE imposta.
    Devolve (m1, m2, sk, C1, C2, r2). Ramo 1 = tensao ALTA (s >= sk)."""
    ls, ln = np.log10(s), np.log10(n)
    best = None
    lo, hi = ls.min(), ls.max()
    for lk in np.linspace(lo + 1e-9, hi - 1e-9, ngrid):
        hi_m = ls >= lk
        if hi_m.sum() < 2 or (~hi_m).sum() < 2:
            continue
        # continuidade: ln = a + b1*(ls-lk) para ls>=lk ; a + b2*(ls-lk) abaixo
        X = np.zeros((len(ls), 3))
        X[:, 0] = 1.0
        X[:, 1] = np.where(hi_m, ls - lk, 0.0)
        X[:, 2] = np.where(hi_m, 0.0, ls - lk)
        beta, *_ = np.linalg.lstsq(X, ln, rcond=None)
        pred = X @ beta
        ss = float(np.sum((ln - pred) ** 2))
        if best is None or ss < best[0]:
            best = (ss, lk, beta)
    ss, lk, beta = best
    a, b1, b2 = beta
    m1, m2 = -b1, -b2
    sk = 10 ** lk
    C1 = 10 ** (a + m1 * lk)
    C2 = 10 ** (a + m2 * lk)
    r2 = 1 - ss / float(np.sum((ln - ln.mean()) ** 2))
    return dict(m1=float(m1), m2=float(m2), sk=float(sk),
                C1=float(C1), C2=float(C2), r2=float(r2))


def predict(f, s):
    return np.where(s >= f['sk'], f['C1'] * s ** -f['m1'], f['C2'] * s ** -f['m2'])


P('=' * 76)
P('GATES S0-S6 — Su-N BILINEAR (congelados em 3794090)')
P('=' * 76)
for b in ('M16', 'M10'):
    P('')
    P('%s — %d pontos' % (b, len(DATA[b])))
    P('  %8s %10s %10s' % ('delta', 'sigma', 'N_95'))
    for d, N, s, ex in DATA[b]:
        P('  %8.3f %10.1f %10.0f %s' % (d, s, N, '(extrap sigma)' if ex else ''))

s16 = np.array([t[2] for t in DATA['M16']])
n16 = np.array([t[1] for t in DATA['M16']])
s10 = np.array([t[2] for t in DATA['M10']])
n10 = np.array([t[1] for t in DATA['M10']])

f16 = fit_bilinear(s16, n16)
f10 = fit_bilinear(s10, n10)

# --------------------------------------------------------------------- S1
P('')
P('=' * 76)
P('S1 — o bilinear e legitimo em M16 (R2>=0.97 E joelho ESTRITAMENTE dentro)')
P('=' * 76)
P('  M16: m1(alta)=%.2f  m2(baixa)=%.2f  sigma_knee=%.1f MPa  R2(log)=%.4f'
  % (f16['m1'], f16['m2'], f16['sk'], f16['r2']))
P('       C1=%.4g  C2=%.4g   (lei unica dava R2=0.8484)' % (f16['C1'], f16['C2']))
dentro = s16.min() * 1.001 < f16['sk'] < s16.max() * 0.999
s1 = (f16['r2'] >= 0.97) and dentro
P('  faixa de sigma M16: %.1f a %.1f MPa | joelho estritamente dentro: %s'
  % (s16.min(), s16.max(), dentro))
P('  S1 %s' % ('OK' if s1 else 'FALHA'))

# --------------------------------------------------------------------- S2
P('')
P('=' * 76)
P('S2 — o JOELHO transfere entre tamanhos? (CEGO, criterio +-20%)')
P('=' * 76)
P('  M10: m1(alta)=%.2f  m2(baixa)=%.2f  sigma_knee=%.1f MPa  R2(log)=%.4f'
  % (f10['m1'], f10['m2'], f10['sk'], f10['r2']))
dk = abs(f10['sk'] - f16['sk']) / f16['sk']
s2 = dk <= 0.20
P('  joelho M16 = %.1f MPa | joelho M10 = %.1f MPa | diferenca = %.1f%%'
  % (f16['sk'], f10['sk'], 100 * dk))
P('  S2 %s' % ('OK' if s2 else 'FALHA'))

# --------------------------------------------------------------------- S3/S4
P('')
P('=' * 76)
P('S3 — o ramo de ALTO CICLO transfere como RAMO? (zero re-ajuste, +-30%)')
P('=' * 76)
alto = s10 < f16['sk']
baixo = ~alto
P('  pontos M10 abaixo do joelho do M16 (sigma < %.1f): %d de %d'
  % (f16['sk'], int(alto.sum()), len(s10)))
if alto.sum() == 0:
    s3, s3void = False, True
    P('  S3 VOID — nenhum ponto na faixa; o gate nao opinou')
else:
    s3void = False
    P('  %10s %12s %12s %9s' % ('sigma', 'N previsto', 'N medido', 'erro'))
    errs = []
    for s, n in zip(s10[alto], n10[alto]):
        np_ = float(f16['C2'] * s ** -f16['m2'])
        e = np_ / n - 1
        errs.append(e)
        P('  %10.1f %12.0f %12.0f %8.1f%% %s'
          % (s, np_, n, 100 * e, 'ok' if abs(e) <= 0.30 else 'FORA'))
    s3 = all(abs(e) <= 0.30 for e in errs)
    P('  S3 %s' % ('OK' if s3 else 'FALHA'))

P('')
P('=' * 76)
P('S4 — a ASSIMETRIA e estrutura? (hipotese: baixo ciclo FORA de +-30% e razao')
P('     N_M10/N_M16 CRESCE com sigma. Se falhar = BOA NOTICIA)')
P('=' * 76)
fora = []
if baixo.sum():
    P('  %10s %12s %12s %9s' % ('sigma', 'N previsto', 'N medido', 'erro'))
    for s, n in zip(s10[baixo], n10[baixo]):
        np_ = float(f16['C1'] * s ** -f16['m1'])
        e = np_ / n - 1
        fora.append(abs(e) > 0.30)
        P('  %10.1f %12.0f %12.0f %8.1f%% %s'
          % (s, np_, n, 100 * e, 'FORA' if abs(e) > 0.30 else 'dentro'))
# monotonia da razao dentro da faixa comum
ls16, ln16 = np.log10(s16), np.log10(n16)
raz = []
for s, n in zip(s10, n10):
    if ls16.min() <= np.log10(s) <= ls16.max():
        raz.append((float(s), float(n / 10 ** np.interp(np.log10(s), ls16, ln16))))
P('  razao N_M10/N_M16 na faixa comum: %s'
  % ', '.join('%.0f MPa: %.2f' % r for r in raz))
mono = all(raz[i][1] <= raz[i + 1][1] for i in range(len(raz) - 1)) if len(raz) > 1 else None
s4 = bool(fora) and all(fora) and bool(mono)
P('  todos os pontos de baixo ciclo FORA: %s | razao monotona crescente: %s'
  % (bool(fora) and all(fora), mono))
P('  S4 %s%s' % ('CONFIRMADA' if s4 else 'NAO confirmada',
                 '' if s4 else '  <- BOA NOTICIA: a assimetria nao e estrutural'))

# --------------------------------------------------------------------- S5
P('')
P('=' * 76)
P('S5 — o sun_life() do engine reproduz o ajuste? (1e-9 relativo)')
P('=' * 76)
mat = JointMaterial(
    fat_C1=f16['C1'] * 1e6 ** f16['m1'], fat_m1=f16['m1'],
    fat_C2=f16['C2'] * 1e6 ** f16['m2'], fat_m2=f16['m2'],
    fat_sigma_knee=f16['sk'] * 1e6,
    fat_sigma_endurance=min(s16.min(), s10.min()) * 1e6 * 0.5)
worst = 0.0
for s in np.concatenate([s16, s10]):
    mine = float(predict(f16, np.array([s]))[0])
    eng = sun_life(float(s) * 1e6, mat)
    worst = max(worst, abs(eng - mine) / mine)
s5 = worst <= 1e-9
P('  conversao: C_Pa = C_MPa * 1e6^m  |  pior desvio relativo em 11 pontos: %.2e'
  % worst)
P('  S5 %s' % ('OK' if s5 else 'FALHA'))

P('')
P('=' * 76)
P('VEREDICTO')
P('=' * 76)
P('  S0 OK (pos-processamento puro: escreve so %s)' % OUT.name)
for k, v in (('S1', s1), ('S2', s2),
             ('S3', 'VOID' if s3void else s3), ('S4', s4), ('S5', s5)):
    P('  %s %s' % (k, 'VOID' if v == 'VOID' else ('OK' if v else 'FALHA')))
P('  S6 OK (nada adotado)')
json.dump({'M16': f16, 'M10': f10,
           'gates': {'S1': bool(s1), 'S2': bool(s2),
                     'S3': ('VOID' if s3void else bool(s3)),
                     'S4': bool(s4), 'S5': bool(s5)},
           'razao_faixa_comum': raz,
           'dados': {b: [[t[0], t[2], t[1]] for t in DATA[b]] for b in DATA}},
          open(OUT, 'w'), indent=1)
P('  -> %s' % OUT)
