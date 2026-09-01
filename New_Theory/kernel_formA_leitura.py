"""LEITURA de forma do kernel A (pre-FAIL2) — o que a lei de taxa do dado diz.

Diagnostico, nao fit. Tres perguntas, medidas sobre o store atual:
  (1) A assinatura do grupo (monotono neg->pos, r>=0,90) SOBREVIVE ao
      fingerprint novo e a membresia pos-varredura (11 curvas)?  [§4.43]
  (2) Qual LEI DE TAXA o dado segue na janela pos-assentamento, e qual o
      modelo segue? (expoente local p em  taxa ~ N^-p, mediana por curva)
  (3) Qual CANAL do modelo carrega a perda na janela do erro (decomp do store)?

Membresia pos-varredura: Chu2026 x7 + Yang2019 x2 + Karlsen x1 + Zhang2006 x1
(as 2 Yang metric-limited terminais sairam — L25).

Caveat declarado: decomp lida da grade AMOSTRADA do store (ate 400 pts) — ok
para SHARES em janelas tardias; nao usar no transiente de embedding.
"""
import json, pathlib
import numpy as np

STORE = pathlib.Path('Models/CALIBRATION_AND_VALIDATION/validation_store.json')
GRUPO_A = [
    'chu2026ti_D0p3mm_F0_49kN_test1', 'chu2026ti_D0p4mm_F0_49kN_test2',
    'chu2026ti_D0p4mm_F0_61kN_test7', 'chu2026ti_D0p4mm_F0_73kN_test8',
    'chu2026ti_D0p5mm_F0_49kN_Ra1p6um_test9', 'chu2026ti_D0p5mm_F0_49kN_test3',
    'chu2026ti_D0p7mm_F0_49kN_test4',
    'yang2019_M10_amp0p4_5Hz', 'yang2019_M10_varamp_large_to_small',
    'karlsen2022_M30_HVtorqued_run14p2',
    'zhang2006_fig3_illus_M12x125_20kN_amp0p35',
]
d = json.loads(STORE.read_text(encoding='utf-8'))
P = print
P('=' * 78)
P('(1) ASSINATURA sob o fingerprint atual (%s), membresia pos-varredura (11)'
  % next(iter({v.get("engine_fingerprint") for v in d.values()})))
P('=' * 78)
prof = {}
for cid in GRUPO_A:
    v = d[cid]
    x = np.asarray(v['metric_x'], float)
    r = np.asarray(v['metric_pred'], float) - np.asarray(v['metric_data'], float)
    q = np.array_split(r - r.mean(), 5)              # detrendado, 5 quintis
    prof[cid] = np.array([float(s.mean()) for s in q])
M = np.array([prof[c] for c in GRUPO_A])
P('media do grupo (detrendado): %s' % np.round(M.mean(0), 3))
cc = np.corrcoef(M)
tri = cc[np.triu_indices(len(GRUPO_A), 1)]
P('correlacao par-a-par: min %.2f | mediana %.2f | (n pares %d)'
  % (tri.min(), np.median(tri), len(tri)))
mono = M.mean(0)
P('assinatura monotona neg->pos mantida: %s'
  % bool(np.all(np.diff(mono) > -0.01) and mono[0] < 0 < mono[-1]))

P('')
P('=' * 78)
P('(2) LEI DE TAXA — expoente local p em taxa ~ N^-p (janela pos-assentamento)')
P('=' * 78)
P('%-42s %8s %8s %10s' % ('curva', 'p_dado', 'p_model', 'razao r_fim'))
p_d_all, p_m_all = [], []
for cid in GRUPO_A:
    v = d[cid]
    x = np.asarray(v['metric_x'], float)
    rd = np.asarray(v['metric_data'], float)
    rm = np.asarray(v['metric_pred'], float)
    # janela pos-assentamento: descarta o 1o quintil de N
    k = x > x[0] + 0.2 * (x[-1] - x[0])
    if k.sum() < 4:
        P('%-42s (curva curta demais)' % cid)
        continue

    def pfit(y):
        # taxa local entre pontos consecutivos; p do ajuste log-log
        dx = np.diff(x[k])
        dy = -np.diff(y[k])
        xm = 0.5 * (x[k][1:] + x[k][:-1])
        ok = (dy > 1e-6) & (dx > 0)
        if ok.sum() < 3:
            return float('nan')
        return -float(np.polyfit(np.log10(xm[ok]), np.log10(dy[ok] / dx[ok]), 1)[0])

    pd_, pm_ = pfit(rd), pfit(rm)
    p_d_all.append(pd_)
    p_m_all.append(pm_)
    P('%-42s %8.2f %8.2f %10.3f'
      % (cid[:42], pd_, pm_, (1 - rm[-1]) / max(1 - rd[-1], 1e-9)))
P('MEDIANAS: p_dado = %.2f | p_modelo = %.2f'
  % (np.nanmedian(p_d_all), np.nanmedian(p_m_all)))
P('  p ~ 1  => perda LOG (linear em log N);  p >> 1 => plateau rapido;')
P('  p_modelo > p_dado = o modelo desacelera CEDO demais (arresto precoce)')

P('')
P('=' * 78)
P('(3) DECOMPOSICAO — quem carrega a perda do MODELO no comeco vs no fim')
P('=' * 78)
P('%-42s %-24s %-24s' % ('curva', 'Q1-Q2 (share por mech)', 'Q4-Q5 (share)'))
for cid in GRUPO_A:
    v = d[cid]
    cyc = np.asarray(v['cycles'], float)
    dec = v.get('decomp') or {}
    if not dec:
        P('%-42s (sem decomp)' % cid)
        continue
    x = np.asarray(v['metric_x'], float)
    n1, n2 = x[0] + 0.4 * (x[-1] - x[0]), x[-1]

    def share(n_lo, n_hi):
        out = {}
        for m, arr in dec.items():
            a = np.asarray(arr, float)
            out[m] = float(np.interp(n_hi, cyc, a) - np.interp(n_lo, cyc, a))
        t = sum(max(u, 0.0) for u in out.values()) or 1e-12
        return {m: u / t for m, u in out.items() if u / t > 0.05}

    s1 = share(x[0], n1)
    s2 = share(n1, n2)
    fmt = lambda s: ' '.join('%s:%.0f%%' % (m[:4], 100 * u)
                             for m, u in sorted(s.items(), key=lambda t: -t[1]))
    P('%-42s %-24s %-24s' % (cid[:42], fmt(s1)[:24], fmt(s2)[:24]))

json.dump(dict(perfil_medio=[float(v) for v in mono],
               corr_min=float(tri.min()), corr_med=float(np.median(tri)),
               p_dado=float(np.nanmedian(p_d_all)),
               p_modelo=float(np.nanmedian(p_m_all)),
               p_por_curva={c: [float(a), float(b)] for c, a, b in
                            zip(GRUPO_A, p_d_all, p_m_all)}),
          open('New_Theory/kernel_formA_leitura.json', 'w'), indent=1)
P('')
P('-> New_Theory/kernel_formA_leitura.json')
