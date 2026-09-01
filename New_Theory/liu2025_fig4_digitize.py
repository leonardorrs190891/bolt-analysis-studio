"""Digitalizacao da Fig. 4 do Liu/Yang 2025 — curvas D-N de M10 e M16.

ATENCAO AO QUE A FIG. 4 E': o eixo N NAO e' vida ate a fratura. O artigo declara
(secao 'Test results'): "convert the D-N curve of the loose state WHEN THE CLAMPING
FORCE WAS REDUCED TO 95% OF THE INITIAL PRE-TIGHTENING FORCE into the Su-N curve".
Ou seja N = ciclos ate F/F0 = 0,95. As vidas de FRATURA (1,4e4 a 3,3e5) nem caberiam
no eixo 1..1e5 da figura.

VALIDACAO INTERNA (o motivo de esta figura ser digitalizavel com confianca): ela traz
as DUAS curvas. O ramo M16 pode ser conferido contra o N_95 medido nas nossas proprias
curvas digitalizadas da Fig. 3 — 6 pontos independentes. So se ele bater e' que o ramo
M10, que nao temos de outra fonte, merece credito.

Saida: New_Theory/liu2025_fig4_DN.json
"""
import json, pathlib, sys
import numpy as np
from PIL import Image

IMG = ('C:/Users/leo_r/AppData/Local/Temp/claude/'
       'C--Users-leo-r-OneDrive-BPL-Analitical-BAS-V2/'
       'ed85f878-94d9-4c33-ae32-1ac989594346/scratchpad/liu_figs/p05_Im0.jpg')
OUT = pathlib.Path('New_Theory/liu2025_fig4_DN.json')

# Calibracao MEDIDA dos eixos. Ticks X: 128.5/302.5/477.0/650.5/824.0/998.5 px
# (6 ticks equiespacados = decadas 10^0..10^5). Ticks Y: 24.0/183.0/454.0 px para
# 1.2/0.8/0.4 — espacamento DESIGUAL (159 e 271 px) porque o eixo Y tambem e'
# LOGARITMICO. Conferido: y = A + B*log10(delta) da B = -903.0 pelo 1o intervalo e
# -900.2 pelo 2o (concordancia de 0,3%), enquanto um eixo linear exigiria
# espacamento igual. Ler o Y como linear foi o erro da 1a passada.
X1_PX, X1_VAL = 128.5, 1.0            # esquerda  = 10^0
X2_PX, X2_VAL = 998.5, 1e5            # direita   = 10^5
YA_PX, YA_VAL = 24.0, 1.2             # tick de cima
YB_PX, YB_VAL = 454.0, 0.4            # tick de baixo

# N_95 MEDIDO nas nossas curvas da Fig. 3 (validacao independente do ramo M16)
N95_NOSSO = {0.25: 62500, 0.30: 25000, 0.40: 2000, 0.50: 692, 0.60: 182, 0.80: 91}


def px2n(x):
    return 10 ** (np.log10(X1_VAL) + (x - X1_PX) / (X2_PX - X1_PX)
                  * (np.log10(X2_VAL) - np.log10(X1_VAL)))


import math
_YB = (YB_PX - YA_PX) / (math.log10(YB_VAL) - math.log10(YA_VAL))
_YA = YA_PX - _YB * math.log10(YA_VAL)


def px2d(y):
    return 10 ** ((y - _YA) / _YB)


a = np.asarray(Image.open(IMG).convert('RGB')).astype(int)
r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
masks = {'M10': (b > r + 45) & (b > g + 25) & (b > 80) & (r < 160),
         'M16': (r > b + 55) & (r > g + 55) & (r > 110)}

# dentro da area de plot apenas (fora dela ficam a legenda e os rotulos)
LEG = (slice(0, 200), slice(430, 1000))         # caixa da legenda: excluir
inside = np.zeros(a.shape[:2], bool)
inside[int(YA_PX):725, int(X1_PX):int(X2_PX)] = True
inside[LEG] = False


def marker_centers(m, min_px=90):
    """Marcadores sao BLOBS grossos; a linha que os liga e' fina. Filtra por
    densidade local e agrupa por rotulagem de vizinhanca."""
    m = m & inside
    # densidade local 9x9
    k = 4
    dens = np.zeros(m.shape, int)
    for dy in range(-k, k + 1):
        for dx in range(-k, k + 1):
            dens += np.roll(np.roll(m, dy, 0), dx, 1)
    core = m & (dens >= 70)          # so o miolo dos marcadores sobrevive
    lbl = np.zeros(core.shape, int)
    cur, out = 0, []
    ys, xs = np.nonzero(core)
    seen = set()
    pts = set(zip(ys.tolist(), xs.tolist()))
    for p in list(pts):
        if p in seen:
            continue
        cur += 1
        stack, comp = [p], []
        seen.add(p)
        while stack:
            y, x = stack.pop()
            comp.append((y, x))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    q = (y + dy, x + dx)
                    if q in pts and q not in seen:
                        seen.add(q)
                        stack.append(q)
        if len(comp) >= min_px:
            cy = float(np.mean([c[0] for c in comp]))
            cx = float(np.mean([c[1] for c in comp]))
            out.append((cx, cy, len(comp)))
    return sorted(out)


P = print
P('=' * 74)
P('DIGITALIZACAO DA FIG. 4 (D-N, N = ciclos ate F/F0 = 0,95)')
P('=' * 74)
res = {}
for nome, m in masks.items():
    c = marker_centers(m)
    pts = [(float(px2n(x)), float(px2d(y)), n) for x, y, n in c]
    res[nome] = pts
    P('')
    P('%s — %d marcadores' % (nome, len(pts)))
    P('  %10s %10s %8s' % ('N_95', 'delta(mm)', 'px'))
    for N, d, n in pts:
        P('  %10.0f %10.3f %8d' % (N, d, n))

# ------------------------------------------------------- VALIDACAO do ramo M16
P('')
P('=' * 74)
P('VALIDACAO — ramo M16 contra o N_95 medido nas NOSSAS curvas da Fig. 3')
P('=' * 74)
m16 = sorted(res['M16'], key=lambda t: t[1])
P('%10s %12s %12s %10s' % ('delta_fig4', 'N_95 fig4', 'N_95 nosso', 'razao'))
raz = []
for N, d, _ in m16:
    dd = min(N95_NOSSO, key=lambda k: abs(k - d))
    if abs(dd - d) > 0.06:
        P('%10.3f %12.0f %12s %10s' % (d, N, '-', 'sem par'))
        continue
    q = N / N95_NOSSO[dd]
    raz.append(q)
    P('%10.3f %12.0f %12.0f %10.2f' % (d, N, N95_NOSSO[dd], q))
if raz:
    raz = np.array(raz)
    P('  razao media %.2f  desvio %.0f%%  (1.00 = digitalizacao consistente)'
      % (raz.mean(), 100 * raz.std() / raz.mean()))
json.dump({k: [[p[0], p[1]] for p in v] for k, v in res.items()},
          open(OUT, 'w'), indent=1)
P('')
P('-> %s' % OUT)
