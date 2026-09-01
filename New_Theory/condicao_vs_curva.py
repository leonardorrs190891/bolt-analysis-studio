"""Erro contra a CONDICAO x erro contra a REPLICA. So-leitura."""
import sys, json, collections, itertools
sys.path.insert(0,'src')
import numpy as np
import bolt_analysis_studio.validation.report_html as rh
from bolt_analysis_studio.validation.case_registry import all_records
from bolt_analysis_studio.validation.runner import CaseResult

store=json.load(open('Models/CALIBRATION_AND_VALIDATION/validation_store.json',encoding='utf-8'))
recs=store.get('cases',store); fonte={r.case_id:r.source for r in all_records()}
vc={r.case_id:r.validation_case for r in all_records()}

# familias pela chave ADOTADA hoje
gr=collections.defaultdict(list)
res_de={}
for cid,g in recs.items():
    if cid not in fonte: continue
    s=fonte[cid]
    if cid in rh._SEM_FAMILIA_MECANICA and s not in rh._FONTES_RESOLVIDAS_POR_CHAVE: continue
    try: r=CaseResult.from_dict(g)
    except Exception: continue
    x=getattr(r,'metric_x',None); d=getattr(r,'metric_data',None); p=getattr(r,'metric_pred',None)
    if not (x and d and p and len(x)==len(d)==len(p)>=4): continue
    res_de[cid]=(np.asarray(x,float), np.asarray(d,float), np.asarray(p,float))
    cfg=getattr(r,'config_used',None) or {}
    try: k=(s, round(float(cfg.get('delta_mm') or 0),4), round(float(cfg.get('F_amp_N') or 0),1), cfg.get('mode'))
    except Exception: continue
    v=vc.get(cid)
    if v is not None: k=k+tuple(getattr(v,c,None) for c in rh._CAMPOS_VARRIDOS)
    gr[k].append(cid)

fams={k:v for k,v in gr.items() if len(v)>1}
print(f'CONDICOES COM >=2 REPLICAS (pela chave estendida): {len(fams)}\n')
print(f'{"condicao":30s} {"n":>2s} {"banda_dado":>10s} {"disp_MODELO":>11s} {"mod-vs-centro":>13s} {"mod-vs-repl(pior)":>17s}')
print('-'*92)
linhas=[]
for k,cids in sorted(fams.items(), key=lambda kv: kv[0][0]):
    lo=max(res_de[c][0].min() for c in cids); hi=min(res_de[c][0].max() for c in cids)
    if hi<=lo: continue
    g=np.linspace(lo,hi,60)
    D=np.array([np.interp(g,res_de[c][0],res_de[c][1]) for c in cids])   # dado
    P=np.array([np.interp(g,res_de[c][0],res_de[c][2]) for c in cids])   # modelo
    centro=D.mean(axis=0)
    banda=max(np.abs(D[i]-D[j]).max() for i,j in itertools.combinations(range(len(cids)),2))
    disp_mod=max(np.abs(P[i]-P[j]).max() for i,j in itertools.combinations(range(len(cids)),2))
    mod_centro=np.abs(P.mean(axis=0)-centro).max()
    pior_repl=max(np.abs(P[i]-D[i]).max() for i in range(len(cids)))
    rot=f'{k[0][:20]}'
    print(f'{rot:30s} {len(cids):2d} {banda:10.4f} {disp_mod:11.4f} {mod_centro:13.4f} {pior_repl:17.4f}')
    linhas.append((k[0], cids, banda, disp_mod, mod_centro, pior_repl))
print()
print('LEITURA:')
print('  banda_dado    = maior |replica - replica| na janela comum (o que o DADO nao resolve)')
print('  disp_MODELO   = maior |predicao - predicao| entre membros da MESMA condicao')
print('                  (0 = o modelo preve a CONDICAO; >0 = ele foi ajustado por CURVA)')
print('  mod-vs-centro = |media das predicoes - centro das replicas| (erro contra a CONDICAO)')
print('  mod-vs-repl   = pior |predicao - dado| individual (o que a METRICA de hoje pontua)')
json.dump([{'fonte':a,'cids':b,'banda':float(c),'disp_modelo':float(d),
            'mod_centro':float(e),'pior_repl':float(f)} for a,b,c,d,e,f in linhas],
          open('New_Theory/condicao_vs_curva.json','w',encoding='utf-8'), indent=1)
