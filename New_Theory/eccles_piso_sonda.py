import sys, json
sys.path.insert(0, 'src')
import numpy as np
from bolt_analysis_studio.calibration import provenance as pv
import bolt_analysis_studio.validation.runner as rn
from bolt_analysis_studio.validation.case_registry import record
from bolt_analysis_studio.validation.runner import CaseResult

S = json.load(open('Models/CALIBRATION_AND_VALIDATION/validation_store.json', encoding='utf-8'))
print('%-42s %7s %9s %10s  %s' % ('curva', 'cfg', 'helper', 'plateau?', 'breakdown'))
for c in sorted(x for x in S if x.startswith('eccles2010_')):
    r = CaseResult.from_dict(S[c])
    d = np.asarray(r.metric_data, float)
    ov = rn._effective_overrides(record(c), {})
    fl = ov.get('loose_arrest_floor')
    if fl is None: continue
    h, info = pv.arrest_floor_from_curve(d)
    pl = info.get('plateau')
    print('%-42s %7.3f %9.4f %10s  %s' % (
        c[:42], float(fl), h, pl,
        json.dumps({k: (round(v, 4) if isinstance(v, float) else v)
                    for k, v in info.items() if k != 'plateau'}, ensure_ascii=False)[:74]))
