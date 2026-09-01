"""Lei DENTRO da fonte — controla o confundimento 'r2 = identificar a fonte'."""
import collections, sys
sys.path.insert(0,'src')
import numpy as np
import bolt_analysis_studio.validation.runner as rn
from bolt_analysis_studio.calibration import knowledge_base as kb
from bolt_analysis_studio.validation.case_registry import all_records

VARS=('transverse_displacement_mm','initial_preload_N','frequency_Hz','roughness_Ra_um',
      'grip_length_mm','member_thickness_mm','reassembly_count','axial_force_amplitude_N',
      'external_axial_N','bolt_diameter_mm')
val=collections.defaultdict(dict); meta={}
for r in all_records():
    cid=r.case_id
    g=rn._adopted_for(r.source, cid, getattr(r.validation_case,'bolt_size','') or '')
    if not g: continue
    c=(kb.adopted_config(g) or {}).get('cfg') or {}
    eff={k:v for k,v in c.items() if k!='per_case' and isinstance(v,(int,float)) and not isinstance(v,bool)}
    for tok,d in (c.get('per_case') or {}).items():
        if tok in cid and isinstance(d,dict):
            eff.update({k:v for k,v in d.items() if isinstance(v,(int,float)) and not isinstance(v,bool)})
    for k,v in eff.items(): val[k][cid]=float(v)
    meta[cid]={'fonte':r.source, **{x:float(getattr(r.validation_case,x,0) or 0) for x in VARS}}

print('LEI INTRA-FONTE: constante varia DENTRO da fonte e segue uma variavel varrida?')
print(f'{"constante":20s} {"fonte":20s} {"n":>2s} {"vals":>4s} {"variavel":>26s} {"r2":>6s}')
print('-'*86)
achados=[]
for k,d in val.items():
    porf=collections.defaultdict(list)
    for cid,v in d.items():
        if cid in meta: porf[meta[cid]['fonte']].append(cid)
    for f,cids in porf.items():
        ys=[d[c] for c in cids]
        if len(cids)<4 or len(set(ys))<3: continue
        y=np.array(ys); y2=np.log(y) if (y>0).all() else y
        for x_ in VARS:
            x=np.array([meta[c][x_] for c in cids])
            if len(set(x))<3 or (x<=0).any(): continue
            X=np.log(x)
            r2=np.corrcoef(X,y2)[0,1]**2
            if r2>=0.75: achados.append((r2,k,f,len(cids),len(set(ys)),x_))
for r2,k,f,n,nv,x_ in sorted(achados, reverse=True)[:14]:
    print(f'{k:20s} {f[:20]:20s} {n:2d} {nv:4d} {x_[:26]:>26s} {r2:6.3f}')
if not achados: print('  NENHUMA constante segue lei intra-fonte com r2>=0.75')
print()
print(f'candidatos intra-fonte com r2>=0.75: {len(achados)}')
