"""Gates A1/A2/A3 da adocao LIU_2025 (prereg CONGELADO em 8ec2521).

A1 (CEGO) — as 7 curvas LIU_2025, metrica canonica pos-trim: tripe 7/7 E nenhuma
     piora > +0.01 em MAE (PR-37'). Risco declarado: amp0p3/amp0p8/fig2 tem a
     rampa DENTRO da janela da metrica (5679/3569/~69 ciclos).
A2 — as 195 curvas de fora: metricas IDENTICAS (ignora generated_at e
     engine_fingerprint, que muda legitimamente com adocao).
A3 — fingerprint NOVO e UNICO nos 203 (!= 4f5bedfbace4).
A4 — informacional: res.max full-curve por curva LIU_2025 + canal fatigue na
     decomposicao.

Uso: py -3.12 New_Theory/liu2025_adocao_gates.py <store_pre_adocao.json>
"""
import sys, json, pathlib
import numpy as np

STORE = pathlib.Path('Models/CALIBRATION_AND_VALIDATION/validation_store.json')
old = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'))
new = json.loads(STORE.read_text(encoding='utf-8'))
LIU = sorted(c for c in new if c.startswith('liu2025_M16_'))
TRIPE = lambda m, x: (m is not None and x is not None and m <= 0.10 and x < 0.10)
IGN = {'generated_at', 'engine_fingerprint'}

P = print
P('=' * 78)
P('GATES DA ADOCAO LIU_2025 (prereg 8ec2521)')
P('=' * 78)
P('casos: %d | grupo LIU_2025: %d' % (len(new), len(LIU)))

# ----------------------------------------------------------------------- A1
P('')
P('A1 (CEGO) — tripe 7/7 e nenhuma piora > +0.01 em MAE pos-trim')
P('%-28s %-17s %-17s %9s %7s %s'
  % ('curva', 'antes (mae/max)', 'depois (mae/max)', 'dMAE', 'tripe', ''))
a1 = True
for c in LIU:
    o, n = old[c], new[c]
    dm = n['mae'] - o['mae']
    trip = TRIPE(n['mae'], n['maxerr'])
    ok = trip and dm <= 0.01
    a1 &= ok
    P('%-28s %-17s %-17s %+9.4f %7s %s'
      % (c.split('M16_')[1], '%.4f/%.4f' % (o['mae'], o['maxerr']),
         '%.4f/%.4f' % (n['mae'], n['maxerr']), dm,
         'PASSA' if trip else 'FALHA', 'ok' if ok else '<<< VIOLA'))
P('  A1: %s' % ('OK' if a1 else 'FALHA -> REVERTER (ramo pre-declarado)'))

# ----------------------------------------------------------------------- A2
P('')
fora = [c for c in new if c not in LIU]


def eq(a, b):
    if isinstance(a, float) or isinstance(b, float):
        if a is None or b is None:
            return a is b
        return (a == b) or (np.isnan(a) and np.isnan(b))
    if isinstance(a, list):
        return len(a) == len(b) and all(eq(x, y) for x, y in zip(a, b))
    if isinstance(a, dict):
        return set(a) == set(b) and all(eq(a[k], b[k]) for k in a)
    return a == b


dif = []
for c in fora:
    ka, kb_ = set(old[c]) - IGN, set(new[c]) - IGN
    if ka != kb_:
        dif.append((c, 'CHAVES'))
        continue
    for k in sorted(ka):
        if not eq(old[c][k], new[c][k]):
            dif.append((c, k))
            break
a2 = not dif
P('A2 — %d curvas de fora: %d divergem  ->  %s'
  % (len(fora), len(dif), 'OK' if a2 else 'FALHA'))
for d in dif[:8]:
    P('     %s' % (d,))

# ----------------------------------------------------------------------- A3
fps = {v.get('engine_fingerprint') for v in new.values()}
a3 = (len(fps) == 1) and ('4f5bedfbace4' not in fps)
P('')
P('A3 — fingerprint novo e UNICO: %s  %s' % (fps, 'OK' if a3 else 'FALHA'))

# ------------------------------------------------------------------ A4 info
P('')
P('A4 (informacional) — full-curve e canal fatigue')
P('%-28s %10s %12s %s' % ('curva', 'final_pred', 'res.max(pos)', 'fatigue na decomp?'))
for c in LIU:
    n = new[c]
    dec = n.get('decomp') or {}
    fat = dec.get('fatigue')
    fat_tot = (fat[-1] if fat else 0.0)
    P('%-28s %10.3f %12.4f %s'
      % (c.split('M16_')[1], n.get('final_pred', float('nan')),
         n.get('maxerr', float('nan')),
         ('SIM (%.3f de F0)' % fat_tot) if fat and fat_tot > 1e-6 else 'nao'))

P('')
P('VEREDICTO: A1 %s | A2 %s | A3 %s'
  % tuple('OK' if g else 'FALHA' for g in (a1, a2, a3)))
json.dump(dict(A1=bool(a1), A2=bool(a2), A3=bool(a3),
               fingerprint=sorted(x for x in fps if x)),
          open('New_Theory/liu2025_adocao_result.json', 'w'), indent=1)
P('-> New_Theory/liu2025_adocao_result.json')
sys.exit(0 if (a1 and a2 and a3) else 1)
