"""MÉTRICA EM VIDA — **REJEITADA** pelos proprios gates (prereg 2026-07-28).

>>> NAO USAR COMO METRICA. Este modulo existe para que a REJEICAO continue
>>> reproduzivel, e para que ninguem re-tente a mesma forma sem ler por que
>>> ela morreu. Ele vive FORA de src/ de proposito: a implementacao chegou a
>>> estar no runner canonico, foi medida, reprovou, e foi revertida.

Prereg: docs/superpowers/specs/2026-07-28-metrica-em-vida-prereg.md (gates
congelados em 3a26b4a, ANTES da implementacao).
Resultado: New_Theory/metrica_vida_results.md · saida bruta em
New_Theory/metrica_vida_output.txt.

VEREDICTO: M2 FALHA (o CLIFF passa) · M3 FALHA (4 de 6 viradas em trecho raso)
· M1 FALHA (3 curvas planas se mexem) · M0 FALHA (desvio 4.7e-2, nao 1e-6).
Ramo pre-declarado para M2 falso: "a metrica nao distingue mais formas => MORRE,
independentemente do resto".

CAUSA UNICA das quatro falhas, medida:

    A fuga horizontal corre pela inclinacao do MODELO, nao pela do DADO.

Em jcsr2023_plain_outdoor N=150 o dado esta PLANO (inclinacao 0,000, estabilizou
em 0,729) e o modelo esta DESPENCANDO (5,2e-3/ciclo). O residuo vertical e'
0,128 — o modelo colapsou cedo demais, que e' o modo de falha que a campanha
mais precisa detectar (§4.8, "colapso por wear excessivo"). Mas a queda do
proprio modelo VARRE o valor 0,729 poucos ciclos antes, entao a distancia
ortogonal acha um ponto vizinho e reporta 0,081. A metrica PERDOA colapso
prematuro. O mesmo mecanismo faz o cliff passar (a queda vertical dele varre
todos os valores de r perto do fim) e produz as viradas em trecho raso.

LICAO DE FORMA (para quem tentar de novo): distancia ao CONJUNTO de pontos da
curva do modelo e' o objeto errado, porque deixa o modelo "chegar perto" por um
caminho que nao corresponde ao mesmo instante. O objeto certo e' a
CORRESPONDENCIA POR NIVEL — o N em que o dado atinge r* contra o N em que o
modelo atinge r* — que foi o que o gate G1 do prereg v2 usou, e que ali
DISTINGUIU rampa de cliff (12 vs 8). Ver liu2025_ramp_v2_results.md §3.
"""
import sys, pathlib
import numpy as np

SIGMA_R = 0.02        # erro declarado de leitura em F/F0   (apparatus notes)
SIGMA_N_FRAC = 0.03   # erro declarado de posicionamento de ciclo (fracao de N)


def life_residuals(cd, rd, model_x, model_r,
                   sig_r: float = SIGMA_R, sig_n_frac: float = SIGMA_N_FRAC):
    """Residuo ORTOGONAL em espaco normalizado pela incerteza. REJEITADA.

        d_i       = min_m sqrt( ((r_m-r_i)/sig_r)^2 + ((N_m-N_i)/sig_N_i)^2 )
        residuo_i = d_i * sig_r ;   sinal_i = sinal(r_modelo(N_i) - r_i)
    """
    cd = np.asarray(cd, dtype=float)
    rd = np.asarray(rd, dtype=float)
    model_x = np.asarray(model_x, dtype=float)
    model_r = np.asarray(model_r, dtype=float)
    vert = np.interp(cd, model_x, model_r) - rd
    out = np.empty(len(cd))
    for i in range(len(cd)):
        n_i, r_i = cd[i], rd[i]
        s_n = max(sig_n_frac * abs(float(n_i)), 1e-9)
        lo = int(np.searchsorted(model_x, n_i - 6.0 * s_n))
        hi = int(np.searchsorted(model_x, n_i + 6.0 * s_n)) + 1
        xs, ys = model_x[lo:hi], model_r[lo:hi]
        if len(xs) == 0:
            out[i] = abs(vert[i])
            continue
        stride = max(1, len(xs) // 4000)
        dx = (xs[::stride] - n_i) / s_n
        dy = (ys[::stride] - r_i) / sig_r
        k = int(np.argmin(dx * dx + dy * dy)) * stride
        j0, j1 = max(0, k - 2 * stride), min(len(xs), k + 2 * stride + 1)
        dx = (xs[j0:j1] - n_i) / s_n
        dy = (ys[j0:j1] - r_i) / sig_r
        d = float(np.sqrt(float((dx * dx + dy * dy).min())))
        out[i] = min(d * sig_r, abs(vert[i]))
    return np.copysign(out, np.where(vert == 0.0, 1.0, vert))


# ---------------------------------------------------------------------------
# Reproducao BARATA (~2 min) do gate que matou a proposta: M2, discriminancia.
# Nao depende do store nem de patch algum — usa o arnes do prereg v2.
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    sys.path.insert(0, str(pathlib.Path('src').resolve()))
    from bolt_analysis_studio.validation import runner

    src = pathlib.Path('New_Theory/liu2025_ramp_v2_gates.py').read_text(encoding='utf-8')
    H = {}
    exec(compile(src.split('P = print')[0], 'harness', 'exec'), H)
    CORE = H['CORE'] + ['liu2025_M16_fig2_single']
    WIN = (0.75, 8.0)
    TRIPE = lambda m, x: m <= 0.10 and x < 0.10

    fine = None
    p = pathlib.Path('New_Theory/liu2025_fig2_fine.csv')
    if p.exists():
        a = np.genfromtxt(p, delimiter=',', skip_header=1)
        xx, rr = a[:, 0], a[:, 1] / a[0, 1]
        k = rr >= runner.FLOOR_TRIM
        fine = (xx[k], rr[k] / rr[k][0])

    def both(cid, ramp, ref):
        n = H['n_span'](cid)
        r = H['sim'](cid, n, ramp=ramp)
        x, rd = ref if ref is not None else H['DATA'][cid]
        m = x <= n
        x, rd = x[m], rd[m]
        al = max(np.interp(float(x[0]), np.arange(n + 1), r), 1e-9)
        pred = np.interp(x, np.arange(n + 1), r / al)
        ev = np.abs(pred - rd)
        el = np.abs(life_residuals(x, rd, np.arange(n + 1), r / al))
        return (float(ev.mean()), float(ev.max())), (float(el.mean()), float(el.max()))

    print('M2 -- DISCRIMINANCIA sob a metrica REJEITADA (P=passa tripe, F=falha)')
    print('%-22s %-24s %-24s' % ('', 'VERTICAL (canonica)', 'EM VIDA (rejeitada)'))
    print('%-22s %-24s %-24s' % ('curva / forma', 'mae/max', 'mae/max'))
    falha = False
    for cid in CORE:
        ref = fine if (cid.endswith('fig2_single') and fine is not None) else None
        for nome, ramp in (('sem forma', None),
                           ('rampa', (WIN[0], WIN[1], H['NF_PAPER'][cid])),
                           ('CLIFF', (0.999, 1.0, H['NF_PAPER'][cid]))):
            v, l = both(cid, ramp, ref)
            print('%-22s %-24s %-24s'
                  % ('%s %s' % (cid.split('M16_')[1][:9], nome),
                     '%.3f/%.3f %s' % (*v, 'P' if TRIPE(*v) else 'F'),
                     '%.3f/%.3f %s' % (*l, 'P' if TRIPE(*l) else 'F')))
            if nome == 'CLIFF' and TRIPE(*l):
                falha = True
    print('')
    print('M2 %s -- o cliff %s sob a metrica em vida.'
          % ('FALHA' if falha else 'OK', 'PASSA' if falha else 'continua falhando'))
