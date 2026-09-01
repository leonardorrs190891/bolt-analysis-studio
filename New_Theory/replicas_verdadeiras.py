"""So as que se DECLARAM replica: _repN, _rN, baselineN, *_repeat, e pares declarados."""
import sys, json, re, collections, itertools
sys.path.insert(0,'src')
import numpy as np
from scipy import stats
import bolt_analysis_studio.validation.report_html as rh
from bolt_analysis_studio.validation.case_registry import all_records
from bolt_analysis_studio.validation.runner import CaseResult

store=json.load(open('Models/CALIBRATION_AND_VALIDATION/validation_store.json',encoding='utf-8'))
recs=store.get('cases',store); fonte={r.case_id:r.source for r in all_records()}
vc={r.case_id:r.validation_case for r in all_records()}
RE_REP=re.compile(r'(_rep\d|_r\d(?!\d)|baseline\d|_repeat|_run\d)')
decl=set()
for a,b,_ in rh._PARES_REPLICA_DECLARADOS: decl |= {a,b}

gr=collections.defaultdict(list); dat={}
for cid,g in recs.items():
    if cid not in fonte: continue
    s=fonte[cid]
    if cid in rh._SEM_FAMILIA_MECANICA and s not in rh._FONTES_RESOLVIDAS_POR_CHAVE: continue
    try: r=CaseResult.from_dict(g)
    except Exception: continue
    x=getattr(r,'metric_x',None); d=getattr(r,'metric_data',None)
    if not (x and d and len(x)==len(d)>=6): continue
    dat[cid]=(np.asarray(x,float), np.asarray(d,float))
    cfg=getattr(r,'config_used',None) or {}
    try: k=(s, round(float(cfg.get('delta_mm') or 0),4), round(float(cfg.get('F_amp_N') or 0),1), cfg.get('mode'))
    except Exception: continue
    v=vc.get(cid)
    if v is not None: k=k+tuple(getattr(v,c,None) for c in rh._CAMPOS_VARRIDOS)
    gr[k].append(cid)

print('SO PARES QUE SE DECLARAM REPLICA (sufixo repN/rN/baselineN/repeat/runN, ou par declarado)')
print(f'{"par":54s} {"|d|max":>7s} {"offset":>6s} {"rho":>6s} {"d_ini":>7s} {"d_fim":>7s} veredito')
print('-'*116)
res=[]
for k,cids in sorted(gr.items(), key=lambda kv: kv[0][0]):
    for a,b in itertools.combinations(sorted(cids),2):
        rep = (RE_REP.search(a) and RE_REP.search(b)) or ({a,b} <= decl)
        if not rep: continue
        xa,da=dat[a]; xb,db=dat[b]
        lo=max(xa.min(),xb.min()); hi=min(xa.max(),xb.max())
        if hi<=lo: continue
        g=np.linspace(lo,hi,60); d=np.interp(g,xa,da)-np.interp(g,xb,db)
        off=abs(d.mean())/max(np.abs(d).mean(),1e-12)
        rho=stats.spearmanr(g,d).statistic if len(set(d))>2 else 0.0
        ini=float(d[:6].mean()); fim=float(d[-6:].mean())
        ver=('SIST+CRESCE' if off>0.9 and abs(rho)>0.7 else
             'SIST const' if off>0.9 else 'CRUZAM' if off<0.5 else 'misto')
        pa=a.replace('bauer2024_','').replace('yang2021_','').replace('caccese2009_','').replace('eccles2010_','')
        pb=b.replace('bauer2024_','').replace('yang2021_','').replace('caccese2009_','').replace('eccles2010_','')
        print(f'{(pa[:25]+" x "+pb[:24])[:54]:54s} {np.abs(d).max():7.4f} {off:6.2f} {rho:6.2f} {ini:7.4f} {fim:7.4f} {ver}')
        res.append(dict(fonte=k[0],a=a,b=b,dmax=float(np.abs(d).max()),offset=float(off),
                        rho=float(rho),ini=ini,fim=fim,ver=ver))
print()
c=collections.Counter(r['ver'] for r in res)
print(f'PARES DECLARADOS REPLICA: {len(res)}   ', dict(c))
for f in sorted({r['fonte'] for r in res}):
    sub=[r for r in res if r['fonte']==f]
    cc=collections.Counter(r['ver'] for r in sub)
    print(f'  {f:20s} {len(sub):2d} pares  {dict(cc)}')
json.dump(res, open('New_Theory/replicas_mesma_condicao.json','w',encoding='utf-8'), indent=1)
