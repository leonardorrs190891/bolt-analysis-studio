"""Caracteriza o estagio III (queda rapida) das curvas Liu2025."""
import csv
import numpy as np

BASE = 'Models/CALIBRATION_AND_VALIDATION/curve_library/digitized_csv/'
CASES = [('0.25', 'liu2025_M16_amp0p25.csv', 240000),
         ('0.30', 'liu2025_M16_amp0p3.csv', 180000),
         ('0.40', 'liu2025_M16_amp0p4_tozero.csv', 60000),
         ('0.50', 'liu2025_M16_amp0p5.csv', 30000),
         ('0.60', 'liu2025_M16_amp0p6.csv', 18000),
         ('0.80', 'liu2025_M16_amp0p8.csv', 11500),
         ('fig2', 'liu2025_M16_fig2_single_tozero.csv', 8000)]


def load(f):
    x, y = [], []
    for r in csv.DictReader(open(BASE + f, encoding='utf-8')):
        x.append(float(r['cycle']))
        y.append(float(r['F_over_F0']))
    return np.array(x), np.array(y)


print('%5s %9s %9s %6s %7s %10s %10s %8s' % (
    'amp', 'N_end', 'N_trim', 'frac', 'r_trim', 'slope_II', 'slope_III', 'ratio'))
rows = []
for amp, f, trim in CASES:
    x, y = load(f)
    Nend = x[-1]
    m2 = (x >= 0.05 * trim) & (x <= trim)
    sII = np.polyfit(x[m2], y[m2], 1)[0]
    m3 = x >= trim
    sIII = np.polyfit(x[m3], y[m3], 1)[0] if m3.sum() >= 2 else float('nan')
    rt = float(np.interp(trim, x, y))
    print('%5s %9.0f %9.0f %6.3f %7.4f %10.2e %10.2e %7.0fx' % (
        amp, Nend, trim, trim / Nend, rt, sII, sIII, sIII / sII))
    rows.append((amp, x, y, Nend, trim, rt))

print()
print('--- cauda em coords normalizadas u=(N-Nk)/(Nf-Nk), r/r_k ---')
for amp, x, y, Nend, trim, rk in rows:
    m = x >= trim
    u = (x[m] - trim) / (Nend - trim)
    rr = y[m] / rk
    print('%5s ' % amp + ' '.join('%.2f:%.3f' % (a, b) for a, b in zip(u, rr)))

print()
print('--- teste: cauda ~ (1-u)^q ?  ajuste log-log de (r/rk) vs (1-u) ---')
for amp, x, y, Nend, trim, rk in rows:
    m = (x >= trim) & (x < Nend)
    u = (x[m] - trim) / (Nend - trim)
    rr = y[m] / rk
    ok = (1 - u > 1e-6) & (rr > 1e-6)
    if ok.sum() < 3:
        continue
    q, c = np.polyfit(np.log(1 - u[ok]), np.log(rr[ok]), 1)
    pred = np.exp(c) * (1 - u[ok]) ** q
    print('%5s  q=%.3f  c=%.3f  resid_max=%.4f' % (
        amp, q, np.exp(c), np.abs(pred - rr[ok]).max()))

print()
print('--- N_D (joelho) vs amplitude: lei de potencia N_D = A*delta^-m ---')
amps = [0.25, 0.30, 0.40, 0.50, 0.60, 0.80]
Nf = [327000.0, 252000.0, 78000.0, 38000.0, 24200.0, 14400.0]
Nk = [240000.0, 180000.0, 60000.0, 30000.0, 18000.0, 11500.0]
for lbl, arr in (('N_f  ', Nf), ('N_knee', Nk)):
    m, c = np.polyfit(np.log(amps), np.log(arr), 1)
    pred = np.exp(c) * np.array(amps) ** m
    r2 = 1 - ((np.log(arr) - np.log(pred)) ** 2).sum() / (
        (np.log(arr) - np.log(arr).mean()) ** 2).sum()
    print('%s = %.3e * delta^%.3f   R2(log)=%.4f  max_rel_err=%.1f%%' % (
        lbl, np.exp(c), m, r2, 100 * np.abs(pred / np.array(arr) - 1).max()))
print('N_knee/N_f por amplitude:', ' '.join('%.3f' % (a / b) for a, b in zip(Nk, Nf)))
