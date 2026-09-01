"""O que DIFERE entre replicas hoje, e o espalhamento e' PREVISIVEL do medido?"""
import sys, json, collections, itertools, glob, os
sys.path.insert(0,'src')
import numpy as np
from scipy import stats
import bolt_analysis_studio.validation.report_html as rh
import bolt_analysis_studio.validation.runner as rn
from bolt_analysis_studio.calibration import knowledge_base as kb
from bolt_analysis_studio.validation.case_registry import all_records
from bolt_analysis_studio.validation.runner import CaseResult
from bolt_analysis_studio.validation.inputs import load_full_curve

store=json.load(open('Models/CALIBRATION_AND_VALIDATION/validation_store.json',encoding='utf-8'))
recs=store.get('cases',store)
comp=[r for r in all_records() if r.case_id in recs and rh.caso_no_documento(r.source,r.case_id)]
results={r.case_id: CaseResult.from_dict(recs[r.case_id]) for r in comp}
pisos=rh._pisos_medidos([(r.source,results[r.case_id]) for r in comp])
pontos,solos,barr=rh.condicoes_agregadas(comp,results,pisos)

# reconstroi as familias (mesma chave)
vcs={r.case_id:r.validation_case for r in comp}
gr=collections.defaultdict(list)
for r in comp:
    cid=r.case_id; res=results[cid]
    if not getattr(res,'metric_x',None): continue
    if cid in rh._SEM_FAMILIA_MECANICA and r.source not in rh._FONTES_RESOLVIDAS_POR_CHAVE: continue
    cu=getattr(res,'config_used',None) or {}
    try: k=(r.source, round(float(cu.get('delta_mm') or 0),4), round(float(cu.get('F_amp_N') or 0),1), cu.get('mode'))
    except Exception: continue
    v=vcs.get(cid)
    if v is not None: k=k+tuple(getattr(v,c,None) for c in rh._CAMPOS_VARRIDOS)
    gr[k].append(cid)
fams={k:v for k,v in gr.items() if len(v)>1}

csvs={}
for p in glob.glob('**/*.csv', recursive=True): csvs.setdefault(os.path.basename(p)[:-4], p)

def consts(cid, src):
    g=rn._adopted_for(src, cid, getattr(vcs[cid],'bolt_size','') or '')
    if not g: return {}, None
    c=(kb.adopted_config(g) or {}).get('cfg') or {}
    eff={k:v for k,v in c.items() if k!='per_case' and isinstance(v,(int,float)) and not isinstance(v,bool)}
    for tok,d in (c.get('per_case') or {}).items():
        if tok in cid and isinstance(d,dict):
            eff.update({k:v for k,v in d.items() if isinstance(v,(int,float)) and not isinstance(v,bool)})
    return eff, g

print('=== 1. O QUE DIFERE ENTRE REPLICAS HOJE (constantes por curva) ===')
print(f'{"condicao":24s} {"n":>2s} {"grupos":>6s} {"const iguais?":>13s}  campos que DIFEREM')
for k,cids in sorted(fams.items(), key=lambda kv:(kv[0][0], -len(kv[1]))):
    E=[]; G=set()
    for c in cids:
        e,g=consts(c, k[0]); E.append(e); G.add(g)
    campos=set().union(*[set(e) for e in E]) if E else set()
    difs=[f for f in sorted(campos) if len({e.get(f) for e in E})>1]
    print(f'{k[0][:24]:24s} {len(cids):2d} {len(G):6d} {"SIM" if not difs else "NAO":>13s}  {difs[:5] if difs else "-"}')

print()
print('=== 2. O ESPALHAMENTO E PREVISIVEL DO QUE FOI MEDIDO? ===')
print('   y0 = valor inicial da CSV crua (o aperto ALCANCADO, medido por especime)')
print(f'{"condicao":22s} {"n":>2s} {"y0 spread":>9s} {"banda":>7s} {"r2(dy, dy0)":>11s} {"resta":>7s}  leitura')
print('-'*104)
for k,cids in sorted(fams.items(), key=lambda kv:(kv[0][0],-len(kv[1]))):
    C={}
    for c in cids:
        if c not in csvs: continue
        try: x,y=load_full_curve(csvs[c])
        except Exception: continue
        x=np.asarray(x,float); y=np.asarray(y,float)
        v=vcs[c]; off=float(getattr(v,'csv_x_offset',0) or 0); sc=float(getattr(v,'csv_x_scale',1) or 1)
        x=np.clip((x-off)*sc,0,None)
        if len(x)>=5: C[c]=(x,y)
    if len(C)<3: continue          # r2 com n=2 e' 1,0 por construcao
    lo=max(x.min() for x,_ in C.values()); hi=min(x.max() for x,_ in C.values())
    if hi<=lo: continue
    g=np.linspace(lo,hi,40)
    Y={c:np.interp(g,*C[c]) for c in C}
    y0={c:float(C[c][1][0]) for c in C}
    m=np.mean([Y[c] for c in C],axis=0); m0=np.mean(list(y0.values()))
    dy=[]; dy0=[]
    for c in C:
        dy.append(float(np.mean(Y[c]-m))); dy0.append(y0[c]-m0)
    r2=np.corrcoef(dy0,dy)[0,1]**2 if len(set(dy0))>2 else float('nan')
    banda=max(np.abs(Y[a]-Y[b]).max() for a,b in itertools.combinations(C,2))
    # residual apos remover o shift previsto por y0 (regressao simples)
    if len(set(dy0))>2:
        b1=np.polyfit(dy0,dy,1)[0]
        Yc={c: Y[c]-b1*(y0[c]-m0) for c in C}
        resta=max(np.abs(Yc[a]-Yc[b]).max() for a,b in itertools.combinations(C,2))
    else: resta=banda
    lt=('y0 EXPLICA a maior parte' if r2>=0.6 and resta<0.7*banda else
        'y0 explica em parte' if r2>=0.3 else 'y0 NAO explica')
    sp=max(y0.values())-min(y0.values())
    print(f'{k[0][:22]:22s} {len(C):2d} {sp:9.4f} {banda:7.4f} {r2:11.3f} {resta:7.4f}  {lt}')
