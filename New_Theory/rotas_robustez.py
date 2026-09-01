import collections, sys, json
sys.path.insert(0,'src')
import numpy as np
import bolt_analysis_studio.validation.runner as rn
from bolt_analysis_studio.calibration import knowledge_base as kb
from bolt_analysis_studio.validation.case_registry import all_records

grupos=collections.defaultdict(list); cfgs={}
for r in all_records():
    g=rn._adopted_for(r.source, r.case_id, getattr(r.validation_case,'bolt_size','') or '')
    if not g: continue
    grupos[g].append(r.case_id)
    cfgs[g]=(kb.adopted_config(g) or {}).get('cfg') or {}

um=[g for g,v in grupos.items() if len(v)==1]
print(f'=== ROTA 1: colapsar grupos IDENTICOS (custo ZERO de exatidao) ===')
print(f'grupos de 1 curva: {len(um)}')
# assinatura do cfg SEM per_case (o per_case e' por token, entao compara-se o efetivo)
def sig(g):
    c=dict(cfgs[g]); per=c.pop('per_case',None)
    if isinstance(per,dict):
        for tok,d in per.items():
            if isinstance(d,dict):
                for k,v in d.items(): c[k]=v
    return json.dumps({k:v for k,v in sorted(c.items())}, sort_keys=True, default=str)
por_sig=collections.defaultdict(list)
for g in grupos: por_sig[sig(g)].append(g)
dup=[v for v in por_sig.values() if len(v)>1]
print(f'grupos com cfg efetivo IDENTICO a outro: {sum(len(v) for v in dup)} em {len(dup)} classes')
for v in sorted(dup, key=len, reverse=True)[:6]:
    print(f'   {len(v)} grupos identicos: {[x[:26] for x in v[:4]]}')
economia=sum(len(v)-1 for v in dup)
print(f'>>> grupos redutiveis SEM tocar em numero nenhum: {economia}')

print()
print('=== ROTA 2: constantes gastas onde o DADO NAO discrimina ===')
banda=json.load(open('New_Theory/condicao_vs_curva.json',encoding='utf-8'))
b_por_fonte={}
for e in banda: b_por_fonte.setdefault(e['fonte'],[]).append(e['banda'])
fonte_de={r.case_id:r.source for r in all_records()}
gr_por_fonte=collections.Counter()
k_por_fonte=collections.Counter()
for g,cids in grupos.items():
    f=fonte_de[cids[0]]
    gr_por_fonte[f]+=1
    c=cfgs[g]
    n=sum(1 for k,v in c.items() if k!='per_case' and isinstance(v,(int,float)) and not isinstance(v,bool))
    n+=sum(len(d) for d in (c.get('per_case') or {}).values() if isinstance(d,dict))
    k_por_fonte[f]+=n
print(f'{"fonte":22s} {"banda":>7s} {"grupos":>7s} {"constantes":>11s}  leitura')
for f,bs in sorted(b_por_fonte.items(), key=lambda kv:-max(kv[1])):
    bmax=max(bs)
    lt=('DADO NAO DISCRIMINA — constante gasta em ruido' if bmax>0.20 else
        'banda media' if bmax>0.06 else 'dado bom — constante bem gasta')
    print(f'  {f[:20]:20s} {bmax:7.4f} {gr_por_fonte[f]:7d} {k_por_fonte[f]:11d}  {lt}')
