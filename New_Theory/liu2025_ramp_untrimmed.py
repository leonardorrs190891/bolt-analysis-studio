"""Quanto o modelo erra na cauda que o trim esconde (Liu2025).

Roda os 7 casos pelo runner canonico e recomputa a metrica em DUAS janelas:
 (a) trimada (o numero publicado)  (b) curva inteira (o que o trim esconde)
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path('src').resolve()))

import numpy as np
from bolt_analysis_studio.validation import runner
from bolt_analysis_studio.validation.case_registry import record, all_records
from bolt_analysis_studio.validation.inputs import load_full_curve, repo_root

CIDS = [r.case_id for r in all_records() if 'liu2025' in r.case_id.lower()]
print('casos:', CIDS)
print()

hdr = ('%-24s %8s %8s | %6s %7s %9s | %6s %7s %9s %8s')
print(hdr % ('case', 'N_trim', 'N_end', 'MAE_t', 'max_t', 'at_t',
             'MAE_all', 'max_all', 'at_all', 'dfinal'))
tot = []
for cid in CIDS:
    rec = record(cid)
    res = runner.simulate_case(rec)
    if not res.ok:
        print(cid, 'ERRO', res.error)
        continue
    cyc = np.array(res.cycles)
    ratio = np.array(res.ratio)
    trim = res.config_used.get('trim_n_max')

    rel = rec.csv_path.relative_to(repo_root()).as_posix()
    cx, cr = load_full_curve(rel)
    cr = cr / cr[0]
    keep = cr >= runner.FLOOR_TRIM
    cx, cr = cx[keep], cr[keep]
    cr = cr / cr[0]

    # alinhamento identico ao runner: no 1o ponto do dado da JANELA
    def metric(mask):
        cd, rd = cx[mask], cr[mask]
        n0 = float(cd[0])
        al = max(np.interp(n0, cyc, ratio), 1e-9)
        pred = np.interp(cd, cyc, ratio / al)
        e = np.abs(pred - rd)
        k = int(np.argmax(e))
        return float(e.mean()), float(e[k]), float(cd[k]), pred, rd, cd

    mt = metric(cx <= trim) if trim else (None,) * 6
    ma = metric(cx <= cx[-1])
    print(hdr % (cid, '%.0f' % (trim or 0), '%.0f' % cx[-1],
                 '%.4f' % mt[0], '%.4f' % mt[1], '%.0f' % mt[2],
                 '%.4f' % ma[0], '%.4f' % ma[1], '%.0f' % ma[2],
                 '%+.3f' % (ma[3][-1] - ma[4][-1])))
    tot.append((cid, mt, ma, cx, cr, cyc, ratio, trim))

print()
print('=== perfil do residuo na cauda (pos-trim): dado vs modelo ===')
for cid, mt, ma, cx, cr, cyc, ratio, trim in tot:
    m = cx >= (trim or 0)
    n0 = float(cx[0])
    al = max(np.interp(n0, cyc, ratio), 1e-9)
    pred = np.interp(cx[m], cyc, ratio / al)
    print('%-24s' % cid)
    print('   N     ' + ' '.join('%8.0f' % v for v in cx[m]))
    print('   dado  ' + ' '.join('%8.3f' % v for v in cr[m]))
    print('   modelo' + ' '.join('%8.3f' % v for v in pred))
    print('   erro  ' + ' '.join('%+8.3f' % v for v in (pred - cr[m])))
