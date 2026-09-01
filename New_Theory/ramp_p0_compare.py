"""P0/P2/P6 do prereg ramp-capability: compara o store re-simulado (engine COM
o codigo da rampa, defaults inertes) contra o backup pre-mudanca.

Criterio: TODOS os campos identicos exceto `generated_at` (timestamp).
P2 = LI_2022_TRIBOINT listado explicitamente (unica fonte com cliff adotado).

Uso: py -3.12 New_Theory/ramp_p0_compare.py <backup.json>
"""
import sys, json, pathlib
import numpy as np

STORE = pathlib.Path('Models/CALIBRATION_AND_VALIDATION/validation_store.json')
old = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'))
new = json.loads(STORE.read_text(encoding='utf-8'))

IGN = {'generated_at'}
P = print
P('casos: backup %d | novo %d' % (len(old), len(new)))
assert set(old) == set(new), 'conjuntos de casos diferem!'


def eq(a, b):
    if type(a) is not type(b) and not (isinstance(a, (int, float))
                                       and isinstance(b, (int, float))):
        return False
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
for cid in old:
    ka = set(old[cid]) - IGN
    kb = set(new[cid]) - IGN
    if ka != kb:
        dif.append((cid, 'CHAVES', sorted(ka ^ kb)))
        continue
    for k in sorted(ka):
        if not eq(old[cid][k], new[cid][k]):
            dif.append((cid, k, None))

P('divergencias (fora generated_at): %d' % len(dif))
for d in dif[:12]:
    P('   ', d)

li = [c for c in new if 'li2022ti' in c]
P('')
P('P2 — LI_2022_TRIBOINT (%d casos, cliff adotado):' % len(li))
for c in sorted(li):
    o, n = old[c], new[c]
    same = all(eq(o.get(k), n.get(k)) for k in
               ('mae', 'maxerr', 'resid_std', 'align', 'final_pred'))
    P('   %-38s mae %.4f  %s' % (c, n.get('mae') or float('nan'),
                                 'IDENTICO' if same else 'DIFERE <<<'))

fps = {v.get('engine_fingerprint') for v in new.values()}
P('')
P('fingerprint: %s' % fps)
ok = (not dif) and fps == {'4f5bedfbace4'}
P('')
P('P0/P2/P6: %s' % ('OK — bit-identico (exceto timestamps)' if ok else 'FALHA'))
sys.exit(0 if ok else 1)
