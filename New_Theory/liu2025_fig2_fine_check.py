"""Teste DIRETO da hipotese DATA-LIMITED (§4.44) na unica curva onde o dado
pode ser recuperado: fig2_single, re-digitalizada fina (134 pts, 45 abaixo de
F/F0=0,33 contra 2 do CSV canonico).

A pergunta: quando o dado passa a existir na cauda, a forma da rampa ACERTA?
Se sim, o rotulo "data-limited" se sustenta -- o que faltava era o dado.
Se nao, a fonte e' data-limited E form-limited, e o trim vira permanente.

fig2_single NAO e' curva de gate no prereg v2 (G5, informacional por decisao
pre-declarada -- e' a pior curva da fonte). Isto e' medicao, nao gate.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path('src').resolve()))
import numpy as np

import importlib.util
spec = importlib.util.spec_from_file_location(
    'v2', pathlib.Path('New_Theory/liu2025_ramp_v2_gates.py'))

# reusa SO o arnes (build/sim/crossing), sem re-executar os gates
src = pathlib.Path('New_Theory/liu2025_ramp_v2_gates.py').read_text(encoding='utf-8')
H = {}
exec(compile(src.split('P = print')[0], 'harness', 'exec'), H)

CID = 'liu2025_M16_fig2_single'
NF = H['NF_PAPER'][CID]
FLOOR = H['runner'].FLOOR_TRIM
WIN = (0.75, 8.0)                      # par vencedor do G1 (nucleo amp0p4/5/6)


def load(path):
    a = np.genfromtxt(path, delimiter=',', skip_header=1)
    x, r = a[:, 0], a[:, 1]
    r = r / r[0]
    k = r >= FLOOR                     # mesma convencao do runner
    return x[k], r[k] / r[k][0]


CANON = H['DATA'][CID]
FINE = load('New_Theory/liu2025_fig2_fine.csv')
print('curva          n_pts  N_fim   r_fim   pts abaixo de 0.33')
for nome, (x, r) in (('canonica', CANON), ('fina', FINE)):
    print('%-14s %5d %6.0f  %.4f   %d' % (nome, len(x), x[-1], r[-1], int((r < 0.33).sum())))

n_max = int(max(FINE[0][-1], CANON[0][-1], NF))


def metric(r_model, ref):
    x, rd = ref
    m = x <= n_max
    x, rd = x[m], rd[m]
    al = max(np.interp(float(x[0]), np.arange(len(r_model)), r_model), 1e-9)
    p = np.interp(x, np.arange(len(r_model)), r_model / al)
    e = np.abs(p - rd)
    return float(e.mean()), float(e.max()), float(np.std(p - rd)), float(x[int(np.argmax(e))])


print('')
print('%-26s %-30s %-30s' % ('config', 'vs curva CANONICA (16pt)', 'vs curva FINA (134pt)'))
print('%-26s %-30s %-30s' % ('', 'MAE / res.max @N', 'MAE / res.max @N'))
for nome, ramp in (('sem forma', None),
                   ('rampa D_on=0.75 q=8', (WIN[0], WIN[1], NF)),
                   ('cliff D_on=0.999 q=1', (0.999, 1.0, NF))):
    r = H['sim'](CID, n_max, ramp=ramp)
    a = metric(r, CANON)
    b = metric(r, FINE)
    print('%-26s %-30s %-30s' % (
        nome, '%.4f / %.4f @%.0f' % (a[0], a[1], a[3]),
        '%.4f / %.4f @%.0f' % (b[0], b[1], b[3])))

print('')
print('TRIPE (MAE<=0.10 E res.max<0.10) na curva FINA, sem trim algum:')
for nome, ramp in (('sem forma', None), ('rampa', (WIN[0], WIN[1], NF)),
                   ('cliff', (0.999, 1.0, NF))):
    r = H['sim'](CID, n_max, ramp=ramp)
    b = metric(r, FINE)
    print('  %-10s MAE %.4f  res.max %.4f  ->  %s'
          % (nome, b[0], b[1], 'PASSA' if (b[0] <= 0.10 and b[1] < 0.10) else 'FALHA'))

print('')
print('Cruzamentos em VIDA na curva FINA (tolerancia do prereg v2 = 0.15*Delta_col = %.0f):'
      % H['tol'](CID))
xs = np.arange(n_max + 1)
r_ramp = H['sim'](CID, n_max, ramp=(WIN[0], WIN[1], NF))
al = max(np.interp(float(FINE[0][0]), xs, r_ramp), 1e-9)
ya = r_ramp / al
print('%8s %10s %10s %10s %s' % ('r*', 'N_dado', 'N_modelo', 'erro', ''))
for lvl in [0.80, 0.70, 0.60, 0.50, 0.40, 0.30, 0.20]:
    nd = H['crossing'](FINE[0], FINE[1], lvl)
    nm = H['crossing'](xs, ya, lvl)
    if nd is None or nm is None:
        print('%8.2f %10s %10s' % (lvl, '--' if nd is None else '%.0f' % nd,
                                   '--' if nm is None else '%.0f' % nm))
        continue
    print('%8.2f %10.0f %10.0f %+10.0f %s'
          % (lvl, nd, nm, nm - nd, 'ok' if abs(nm - nd) <= H['tol'](CID) else 'XX'))
