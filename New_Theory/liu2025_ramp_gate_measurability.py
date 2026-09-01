"""O gate G1 (res.max < 0.10) e' MENSURAVEL nesta fonte?

apparatus_notes/liu2025_scirep_M16.md declara o erro de digitalizacao:
  "+-0.02 em F/F0, +-3% no posicionamento de ciclo"
No trecho de colapso a curva e' quase VERTICAL, entao +-3% em N vira um erro
GRANDE em r. Se esse erro sozinho > 0.10, nenhum modelo pode passar o gate ali.
"""
import csv
import numpy as np

BASE = 'Models/CALIBRATION_AND_VALIDATION/curve_library/digitized_csv/'
CASES = [('0.25', 'liu2025_M16_amp0p25.csv', 240000.0),
         ('0.30', 'liu2025_M16_amp0p3.csv', 180000.0),
         ('0.40', 'liu2025_M16_amp0p4.csv', 60000.0),
         ('0.50', 'liu2025_M16_amp0p5.csv', 30000.0),
         ('0.60', 'liu2025_M16_amp0p6.csv', 18000.0),
         ('0.80', 'liu2025_M16_amp0p8.csv', 11500.0),
         ('fig2', 'liu2025_M16_fig2_single.csv', 8000.0)]
DX = 0.03      # +-3% no posicionamento de ciclo (declarado)
DY = 0.02      # +-0.02 em F/F0 (declarado)


def load(f):
    x, y = [], []
    for r in csv.DictReader(open(BASE + f, encoding='utf-8')):
        x.append(float(r['cycle'])); y.append(float(r['F_over_F0']))
    return np.array(x), np.array(y)


print('%-6s %10s %12s %10s %9s %8s' % (
    'amp', 'N_fim', '|dr/dN|_max', 'dN=3%N', 'dr_de_dN', 'dr_tot'))
print('       ' + '-' * 62)
worst = []
for amp, f, nk in CASES:
    x, y = load(f)
    m = x >= nk
    xt, yt = x[m], y[m]
    sl = np.abs(np.diff(yt) / np.diff(xt))
    k = int(np.argmax(sl))
    dN = DX * x[-1]
    dr = sl[k] * dN
    tot = np.hypot(dr, DY)
    worst.append(tot)
    print('%-6s %10.0f %12.3g %10.0f %9.3f %8.3f  %s' % (
        amp, x[-1], sl[k], dN, dr, tot,
        'GATE INVIAVEL' if tot > 0.10 else 'ok'))

print()
print('  dr_tot = incerteza do PROPRIO DADO no trecho de colapso, so das duas')
print('  tolerancias declaradas na nota de aparato. Gate G1 pede res.max < 0.100.')
print('  Curvas em que a incerteza do dado ja excede o gate: %d de %d.'
      % (sum(1 for w in worst if w > 0.10), len(worst)))
print()
print('  Sensibilidade INVERSA (a leitura que o dado suporta): quantos ciclos')
print('  correspondem a um residuo de 0.10 em r, no trecho de colapso?')
print('%-6s %12s %12s' % ('amp', 'dN p/ dr=0.1', '% da vida'))
for amp, f, nk in CASES:
    x, y = load(f)
    m = x >= nk
    xt, yt = x[m], y[m]
    sl = np.abs(np.diff(yt) / np.diff(xt))
    k = int(np.argmax(sl))
    dn = 0.10 / sl[k]
    print('%-6s %12.0f %11.2f%%' % (amp, dn, 100 * dn / x[-1]))
print()
print('  => no colapso, 0.10 de residuo VERTICAL equivale a 0.1-1.5% da vida.')
print('     Exigir res.max<0.10 ali e exigir o relogio com ~1% de precisao,')
print('     contra 44% de scatter de especime medido na propria fonte.')
