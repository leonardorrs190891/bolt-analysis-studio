"""A banda e' condicao diferente ou DURACAO diferente? Banda em ciclo x em vida normalizada."""
import sys, json, collections, itertools, glob, os
sys.path.insert(0,'src')
import numpy as np
from scipy import stats
import bolt_analysis_studio.validation.report_html as rh
from bolt_analysis_studio.validation.case_registry import all_records
from bolt_analysis_studio.validation.inputs import load_full_curve
from bolt_analysis_studio.validation.runner import CaseResult

store=json.load(open('Models/CALIBRATION_AND_VALIDATION/validation_store.json',encoding='utf-8'))
recs=store.get('cases',store); fonte={r.case_id:r.source for r in all_records()}
vc={r.case_id:r.validation_case for r in all_records()}
csvs={}
for p in glob.glob('**/*.csv', recursive=True):
    csvs.setdefault(os.path.basename(p)[:-4], p)
gr=collections.defaultdict(list)
for cid,g in recs.items():
    if cid not in fonte: continue
    s=fonte[cid]
    if cid in rh._SEM_FAMILIA_MECANICA and s not in rh._FONTES_RESOLVIDAS_POR_CHAVE: continue
    cu=g.get('config_used') or {}
    try: k=(s, round(float(cu.get('delta_mm') or 0),4), round(float(cu.get('F_amp_N') or 0),1), cu.get('mode'))
    except Exception: continue
    v=vc.get(cid)
    if v is not None: k=k+tuple(getattr(v,c,None) for c in rh._CAMPOS_VARRIDOS)
    gr[k].append(cid)

print(f'{"condicao":22s} {"n":>2s} {"dur min-max":>16s} {"razao":>6s} {"banda ciclo":>11s} {"banda vida":>10s} {"artefato":>9s}')
print('-'*94)
tot=[]
for k,cids in sorted(gr.items(), key=lambda kv: kv[0][0]):
    if len(cids)<2: continue
    C={}
    for c in cids:
        if c not in csvs: continue
        try:
            x,y=load_full_curve(csvs[c]); x=np.asarray(x,float); y=np.asarray(y,float)
        except Exception: continue
        vcc=vc.get(c)
        off=float(getattr(vcc,'csv_x_offset',0) or 0); sc=float(getattr(vcc,'csv_x_scale',1) or 1)
        x=np.clip((x-off)*sc, 0, None)
        if len(x)>=5 and x.max()>0: C[c]=(x,y)
    if len(C)<2: continue
    dur=[x.max() for x,_ in C.values()]
    lo=max(x.min() for x,_ in C.values()); hi=min(dur)
    if hi<=lo: continue
    g=np.linspace(lo,hi,40); Z={c:np.interp(g,*C[c]) for c in C}
    b_abs=max(np.abs(Z[a]-Z[b]).max() for a,b in itertools.combinations(C,2))
    u=np.linspace(0.05,1.0,40); Y={c:np.interp(u*C[c][0].max(), *C[c]) for c in C}
    b_nrm=max(np.abs(Y[a]-Y[b]).max() for a,b in itertools.combinations(C,2))
    art=100*(1-b_nrm/max(b_abs,1e-9))
    print(f'{k[0][:22]:22s} {len(C):2d} {min(dur):7.0f}-{max(dur):<8.0f} {max(dur)/max(min(dur),1e-9):6.1f}x '
          f'{b_abs:11.4f} {b_nrm:10.4f} {art:8.0f}%')
    tot.append((k[0],len(C),float(min(dur)),float(max(dur)),float(b_abs),float(b_nrm),float(art)))
print()
art=[t[6] for t in tot]
print(f'condicoes medidas: {len(tot)}   artefato de duracao: mediana {np.median(art):.0f}%  '
      f'max {max(art):.0f}%  (>{sum(1 for a in art if a>40)} acima de 40%)')
json.dump(tot, open('New_Theory/duracao_artefato.json','w',encoding='utf-8'), indent=1)
