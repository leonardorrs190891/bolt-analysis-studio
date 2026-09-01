"""Re-digitalizacao FINA da Fig. 2 do Liu 2025 (colapso ate zero).

MOTIVO (§4.44 MODEL_LEGITIMACY, classe DATA-LIMITED): das 7 curvas da fonte, 6
vem da Fig. 3, cujo eixo Y termina em 20 kN = 0,333*F0 -- a cauda simplesmente
NAO EXISTE no artigo e nenhuma re-digitalizacao a recupera (o inset da Fig. 3
amplia o COMECO, 0-5e3 ciclos, nao a cauda). A Fig. 2 e' a excecao: plota o
colapso inteiro ate 0 kN. O CSV atual cobre esse colapso com SEIS pontos
(8800..10000) e o ultimo, (10000, 0.0000), ainda e' descartado pelo nosso
FLOOR_TRIM=0.10 -- ou seja, a metrica ve a curva acabar em 0,300.

METODO: traco por VARREDURA DE LINHA no trecho vertical (por coluna o colapso
tem ~25 px e daria ~25 pontos; por linha da ~300). Banda = envelope de
oscilacao; o traco segue o CENTRO da banda, mesma convencao do CSV original.

VALIDACAO OBRIGATORIA: o traco novo e' comparado aos 16 pontos existentes na
regiao de sobreposicao. Sem concordancia dentro do erro declarado (+-0,02 em
F/F0) nada e' escrito.

Saida: New_Theory/liu2025_fig2_fine.csv (NAO substitui o CSV canonico; adocao
e' decisao separada, com re-simulacao e gate).
"""
import pathlib
import numpy as np
from PIL import Image

PNG = pathlib.Path('New_Theory/variable_explorer/paper_figures/liu_2025__fig2.png')
REF = pathlib.Path('Models/CALIBRATION_AND_VALIDATION/curve_library/'
                   'digitized_csv/liu2025_M16_fig2_single.csv')
OUT = pathlib.Path('New_Theory/liu2025_fig2_fine.csv')

# calibracao medida das marcas de eixo (sonda 2026-07-28)
X0_PX, X0_VAL = 115.5, 0.0            # tick "0"
X1_PX, X1_VAL = 614.5, 10000.0        # tick "1x10^4"
Y0_PX, Y0_VAL = 502.5, 0.0            # tick "0" kN
Y1_PX, Y1_VAL = 58.5, 70.0            # tick "70" kN
CYC_PER_PX = (X1_VAL - X0_VAL) / (X1_PX - X0_PX)
KN_PER_PX = (Y1_VAL - Y0_VAL) / (Y1_PX - Y0_PX)      # negativo (y cresce p/ baixo)

a = np.asarray(Image.open(PNG).convert('RGB')).astype(int)
r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
blue = (b > r + 40) & (b > g + 40) & (b > 90)


def runs(idx, gap=2):
    """agrupa indices contiguos (tolerancia gap) -> lista de arrays."""
    out = []
    for i in idx:
        if out and i - out[-1][-1] <= gap:
            out[-1].append(i)
        else:
            out.append([i])
    return [np.array(o) for o in out]


def px2cyc(x):
    return X0_VAL + (x - X0_PX) * CYC_PER_PX


def px2kn(y):
    return Y0_VAL + (y - Y0_PX) * KN_PER_PX


pts = []                      # (cycle, kN, origem)

# --- 1) trecho raso: varredura por COLUNA (banda ~horizontal) ---------------
for x in range(a.shape[1]):
    ys = np.nonzero(blue[:, x])[0]
    if len(ys) < 2:
        continue
    seg = max(runs(ys), key=len)          # maior run contiguo = a banda
    if len(seg) > 120:                    # banda absurda: nao e' a curva
        continue
    ext_kn = abs(px2kn(seg[-1]) - px2kn(seg[0]))
    if ext_kn > 12.0:                     # trecho ja vertical: linha resolve
        continue
    pts.append((px2cyc(x), px2kn(0.5 * (seg[0] + seg[-1])), 'col'))

# --- 2) trecho vertical: varredura por LINHA -------------------------------
for y in range(a.shape[0]):
    xs = np.nonzero(blue[y, :])[0]
    if len(xs) < 1:
        continue
    seg = max(runs(xs), key=len)
    ext_cyc = abs(px2cyc(seg[-1]) - px2cyc(seg[0]))
    if ext_cyc > 900.0:                   # trecho raso: coluna resolve
        continue
    pts.append((px2cyc(0.5 * (seg[0] + seg[-1])), px2kn(y), 'row'))

pts.sort(key=lambda t: t[0])
cyc = np.array([p[0] for p in pts])
kn = np.array([p[1] for p in pts])
src = [p[2] for p in pts]
print('pontos brutos: %d (coluna %d, linha %d)'
      % (len(pts), src.count('col'), src.count('row')))

# monotonizar em F (a curva e' nao-crescente; ruido de traco viola isso)
kn = np.minimum.accumulate(kn)
cyc = np.maximum.accumulate(cyc)

# NORMALIZACAO: pela pre-carga NOMINAL do artigo (matriz de ensaios: F0=60 kN),
# NAO pelo centro da banda na 1a coluna. Motivo medido: a queda inicial
# 1,00->0,93 acontece em ~2 px (50 ciclos = 2,5 px), entao a banda ja comeca
# visivel em 56,1 kN; normalizar por ela inflaria a curva inteira em ~7%.
# Com F0=60 o traco reproduz o CSV canonico no ponto (3000; 0,8300) EXATAMENTE.
# Mesma convencao do CSV canonico, que ancora (0; 1,0000).
F0_NOM = 60.0
r_new = kn / F0_NOM
m = cyc > 0.0                                 # x < spine => ciclo negativo
cyc, r_new = cyc[m], r_new[m]
cyc = np.concatenate(([0.0], cyc))            # ancora de pre-carga do artigo
r_new = np.concatenate(([1.0], r_new))

# ------------------------------------------------------- VALIDACAO vs o CSV
ref = np.genfromtxt(REF, delimiter=',', skip_header=1)
rc, rr = ref[:, 0], ref[:, 1]

# Criterio de concordancia = MODELO DE ERRO DECLARADO da fonte
# (apparatus_notes: +-0.02 em F/F0 E +-3% no posicionamento de ciclo), aplicado
# no eixo em que cada trecho e' bem-posto -- mesma logica do E1 do prereg v2:
#   trecho RASO   -> compara VERTICAL   (|dr| <= 0.02 + 1px do traco)
#   trecho INGREME-> compara em VIDA    (|dN| <= 3% de N + 1px do traco)
# "ingreme" = onde os +-3% de N ja implicam mais de 0.02 em r, i.e. onde a
# comparacao vertical deixa de ser bem-posta. Nao e' folga: onde o vertical
# vale, ele continua valendo em 0.02.
PX_R = abs(KN_PER_PX) / F0_NOM                 # 1 px em r    ~ 0.0026
PX_N = CYC_PER_PX                              # 1 px em N    ~ 20 ciclos
slope = np.abs(np.gradient(rr, rc))            # |dr/dN| local do CSV
ok = (rc >= cyc[0]) & (rc <= cyc[-1])
pred = np.interp(rc[ok], cyc, r_new)

# ORCAMENTO DE ERRO COMPLETO, projetado no eixo vertical. Quatro termos, todos
# DECLARADOS e nenhum fitado -- dois da fonte (apparatus_notes) e dois da
# rasterizacao. Os termos horizontais entram multiplicados pela inclinacao
# local, que e' como incerteza em N vira incerteza em r:
#     tol(r) = 0.02  +  1px_r  +  |dr/dN| * ( 0.03*N  +  1px_N )
#              ^fonte  ^traco               ^fonte      ^traco
# Onde a curva e' plana isto colapsa em +-0.0226 (criterio estrito); onde e'
# quase vertical, ele reconhece que a comparacao vertical perde sentido -- a
# mesma razao pela qual o gate G1 do prereg v2 pontua em VIDA.
ORC = 0.02 + PX_R + slope[ok] * (0.03 * rc[ok] + PX_N)
print('')
print('VALIDACAO contra os %d pontos do CSV canonico (%d na sobreposicao)'
      % (len(rc), ok.sum()))
print('criterio = orcamento de erro DECLARADO (fonte + rasterizacao)')
print('%8s %8s %8s %9s %9s %8s %9s'
      % ('cycle', 'CSV', 'traco', 'd_r', 'tol_r', 'd/tol', 'd_vida'))
falhas = 0
for c, o, n, t in zip(rc[ok], rr[ok], pred, ORC):
    dev = abs(n - o)
    n_tr = float(np.interp(-o, -r_new, cyc))   # N em que o TRACO atinge r=o
    bad = dev > t
    falhas += bad
    print('%8.0f %8.4f %8.4f %+9.4f %9.4f %8.2f %+9.0f %s'
          % (c, o, n, n - o, t, dev / t, n_tr - c, 'XX' if bad else 'ok'))
print('  pior razao desvio/tolerancia: %.2f' % float((np.abs(pred - rr[ok]) / ORC).max()))

if falhas:
    print('')
    print('REPROVADO: %d ponto(s) fora do erro declarado da fonte.' % falhas)
    print('Nada foi escrito. Investigar calibracao/mascara antes de reusar.')
    raise SystemExit(1)
print('  todos os %d pontos dentro do erro declarado.' % int(ok.sum()))

# ---------------------------------------------------------------- reamostra
# passo fino onde importa: 200 niveis iguais em F entre 1.0 e 0.0
lv = np.linspace(r_new[0], r_new[-1], 200)
xs_ = np.interp(-lv, -r_new, cyc)              # r decrescente -> inverter sinal
keep = np.concatenate(([True], np.diff(xs_) > 0))
lv, xs_ = lv[keep], xs_[keep]

OUT.write_text('cycle,F_over_F0\n'
               + '\n'.join('%.0f,%.4f' % (x, v) for x, v in zip(xs_, lv)) + '\n',
               encoding='utf-8')
print('')
print('APROVADO. %d pontos -> %s' % (len(lv), OUT))
below = (lv < 0.33).sum()
print('  pontos ABAIXO de F/F0=0.33 (a regiao que faltava): %d  (CSV atual: %d)'
      % (below, int((rr < 0.33).sum())))
print('  pontos ABAIXO de FLOOR_TRIM=0.10: %d (serao descartados pela metrica)'
      % (lv < 0.10).sum())
