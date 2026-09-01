"""G3 na FORMA, versao limpa: mede a rampa RELATIVA AO PROPRIO JOELHO.

Coordenadas:  u = (N - N_knee)/(N_f - N_knee)   (0 no joelho, 1 na fratura)
              v = r / r_knee                    (1 no joelho)
Se a rampa e' uma unica funcao, todas as curvas cruzam v no mesmo u.
"""
import csv
import numpy as np

BASE = 'Models/CALIBRATION_AND_VALIDATION/curve_library/digitized_csv/'
# (amp, csv, N_f do artigo, N_knee = trim vigente, r_knee)
CASES = [('0.25', 'liu2025_M16_amp0p25.csv', 330000.0, 240000.0),
         ('0.30', 'liu2025_M16_amp0p3.csv', 250000.0, 180000.0),
         ('0.40', 'liu2025_M16_amp0p4.csv', 77000.0, 60000.0),
         ('0.50', 'liu2025_M16_amp0p5.csv', 38000.0, 30000.0),
         ('0.60', 'liu2025_M16_amp0p6.csv', 24200.0, 18000.0),
         ('0.80', 'liu2025_M16_amp0p8.csv', 14400.0, 11500.0),
         ('fig2', 'liu2025_M16_fig2_single.csv', 10000.0, 8000.0)]


def load(f):
    x, y = [], []
    for r in csv.DictReader(open(BASE + f, encoding='utf-8')):
        x.append(float(r['cycle'])); y.append(float(r['F_over_F0']))
    return np.array(x), np.array(y)


LV = [0.97, 0.94, 0.90, 0.85, 0.80, 0.70, 0.60]
print('u = (N-N_joelho)/(N_f-N_joelho) em que r/r_joelho cruza cada nivel v')
print('%-6s %7s ' % ('amp', 'r_joelho') + ' '.join('%8s' % ('v=%.2f' % L) for L in LV))
tab = []
for amp, f, nf, nk in CASES:
    x, y = load(f)
    rk = float(np.interp(nk, x, y))
    m = x >= nk
    xt, yt = x[m], y[m] / rk
    row = []
    for L in LV:
        idx = np.where(yt <= L)[0]
        if len(idx) == 0 or idx[0] == 0:
            row.append(np.nan); continue
        i = idx[0]
        xc = xt[i - 1] + (xt[i] - xt[i - 1]) * (yt[i - 1] - L) / max(yt[i - 1] - yt[i], 1e-12)
        row.append((xc - nk) / (nf - nk))
    tab.append(row)
    print('%-6s %7.3f ' % (amp, rk) + ' '.join('%8.3f' % v for v in row))
tab = np.array(tab)


def stats(t, label):
    print('%-14s ' % label + ' '.join('%8.3f' % v for v in np.nanmean(t, axis=0)))
    print('%-14s ' % (label + ' sd') + ' '.join('%8.3f' % v for v in np.nanstd(t, axis=0)))
    print('%-14s ' % 'n' + ' '.join('%8d' % v for v in (~np.isnan(t)).sum(axis=0)))


print()
stats(tab, 'todas')
print()
print('sem o amp0p8 (o especime do scatter de 44%: joelho em 0.680, anomalo):')
stats(np.delete(tab, 5, axis=0), 'sem 0.80')
