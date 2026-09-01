"""Varredura das 3 CLASSES (L25) nos 39 form-limited pos-assinatura do S4.

Diagnostico, nao adocao — sem gates. Para cada violador NAO coberto por
excecao assinada, mede as assinaturas operacionais da L25 sobre os vetores da
metrica (store canonico, fingerprint atual):

  DATA-LIMITED    res.max no ULTIMO ponto da referencia E o dado termina em
                  valor de moldura (aqui detectavel: final <= 0.12 ~ FLOOR_TRIM,
                  ou queda terminal abrupta do dado)
  METRIC-LIMITED  no ponto do res.max, o erro de posicionamento de ciclo
                  declarado (+-3% de N) ja vale >= 0.10 em r:
                  |dr/dN|_dado * 0.03 * N >= 0.10  (a aritmetica da §4.44a)
  FORM-LIMITED    o resto — com o perfil (meio-da-curva vs terminal) anotado

Uso: py -3.12 New_Theory/tres_classes_varredura.py
"""
import sys, json, pathlib
import numpy as np

STORE = pathlib.Path('Models/CALIBRATION_AND_VALIDATION/validation_store.json')
EXCECOES = {
    # §A scatter (7)
    'bauer2024_M8_fig6_rep1', 'bauer2024_M8_fig6_rep4', 'bauer2024_M8_fig6_rep5',
    'bauer2024_M8_fig6_rep6', 'bauer2024_M12_fig8_test1', 'bauer2024_M12_fig8_test2',
    'bauer2024_M12_fig8_test3',
    # §C (5)
    'jcsr2023_plain_outdoor', 'jcsr2023_stainless_seawater',
    'yang2021_fig2_typical', 'yang2021_amp0p8mm_ax6kN',
    'liu2020_fig9_zinc_AF0.4mm_P0-18kN',
    # §D eccles violadoras (4)
    'eccles2010_fig6_annotated_4kN_axial', 'eccles2010_fig8d_axial_3p5kN_intermittent',
    'eccles2010_fig8b_axial_0p7kN_intermittent', 'eccles2010_fig8a_no_axial_baseline1',
}

d = json.loads(STORE.read_text(encoding='utf-8'))
P = print
fora = {c: v for c, v in d.items()
        if v.get('mae') is not None
        and not (v['mae'] <= 0.10 and v['maxerr'] < 0.10)}
P('violadores no store: %d | excecoes assinadas encontradas: %d'
  % (len(fora), len(EXCECOES & set(fora))))
alvo = {c: v for c, v in fora.items() if c not in EXCECOES}
P('alvo da varredura (form-limited assinados): %d' % len(alvo))
P('')

rows = []
for cid, v in sorted(alvo.items()):
    x = np.asarray(v['metric_x'], float)
    rd = np.asarray(v['metric_data'], float)
    if len(x) < 3:
        rows.append(dict(cid=cid, classe='sem-vetor', nota='metric_x curto'))
        continue
    at = float(v.get('maxerr_at') or x[-1])
    k = int(np.argmin(np.abs(x - at)))
    g = np.abs(np.gradient(rd, x))
    slope_at = float(g[k])
    incerteza_r = slope_at * 0.03 * max(at, 1.0)      # ±3% de N em unidades de r
    terminal = (k >= len(x) - 1)
    quase_term = (k >= len(x) - 2)
    final_dado = float(rd[-1])
    perto_floor = final_dado <= 0.12
    # queda terminal abrupta do dado (moldura/fim de digitalizacao)
    tail_drop = float(rd[-2] - rd[-1]) if len(rd) >= 2 else 0.0
    tail_gap = float(x[-1] - x[-2]) if len(x) >= 2 else 0.0
    tail_steep = (tail_gap > 0) and (abs(tail_drop / max(tail_gap, 1e-9))
                                     * 0.03 * x[-1] >= 0.10)
    if incerteza_r >= 0.10:
        classe = 'METRIC-limited'
        nota = ('no pico, ±3%% de N ja vale %.2f em r (>=0,10): '
                'nenhuma metrica vertical decide ali' % incerteza_r)
    elif terminal and (perto_floor or tail_steep):
        classe = 'DATA-limited'
        nota = ('res.max no ULTIMO ponto; dado termina em %.3f%s'
                % (final_dado, ' (~FLOOR/moldura)' if perto_floor
                   else ' com queda terminal abrupta'))
    else:
        onde = ('terminal' if terminal else
                ('quase-terminal' if quase_term else
                 'meio da curva (%.0f%% da janela)' % (100 * at / x[-1])))
        classe = 'FORM-limited'
        nota = 'residuo %s; incerteza local %.3f' % (onde, incerteza_r)
    rows.append(dict(cid=cid, classe=classe, mae=v['mae'], maxerr=v['maxerr'],
                     at=at, at_frac=float(at / x[-1]), slope=slope_at,
                     incerteza_r=incerteza_r, final_dado=final_dado, nota=nota))

P('%-42s %-14s %-15s %6s  %s' % ('caso', 'classe', 'mae/max', 'pico@', 'nota'))
cont = {}
for r in rows:
    cont[r['classe']] = cont.get(r['classe'], 0) + 1
    P('%-42s %-14s %-15s %5.0f%%  %s'
      % (r['cid'][:42], r['classe'],
         '%.3f/%.3f' % (r.get('mae', 0), r.get('maxerr', 0)),
         100 * r.get('at_frac', 0), r.get('nota', '')[:72]))
P('')
P('CONTAGEM: %s' % cont)
json.dump(dict(contagem=cont, casos=rows),
          open('New_Theory/tres_classes_result.json', 'w'), indent=1)
P('-> New_Theory/tres_classes_result.json')
