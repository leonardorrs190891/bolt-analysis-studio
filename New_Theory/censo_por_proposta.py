import os, sys, json
sys.path.insert(0, 'src')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from collections import defaultdict
from bolt_analysis_studio.validation import report_html as rh
from bolt_analysis_studio.validation.case_registry import all_records
from bolt_analysis_studio.validation.runner import CaseResult
# classificador CANONICO das camadas de estatuto — o mesmo que a triagem usa.
# Importado, NAO reimplementado: foi reimplementa-lo (em duas camadas) que fez
# este script publicar 19 "abertas" onde a triagem publica 0 form-limited.
from regra_de_parada_triagem import classificar, piso_da_fonte

# O `mapa_das_65_fora.json` e' um RETRATO CONGELADO. Ele continua sendo a fonte
# legitima do mapeamento proposta -> curva (isso e' julgamento, nao medicao),
# mas a PERTINENCIA de cada curva ("ainda esta fora?", "tem estatuto?") tem de
# ser RE-MEDIDA contra o store, senao o script publica o censo do dia em que o
# mapa foi escrito. Defeito medido em 2026-08-09: depois do D-Z e do D-AA ele
# reportava "fora 66 / abertas 32" contra os 63 / 30 do censo canonico, porque
# as 3 curvas que fecharam seguiam listadas. E' o §4.43 dentro da ferramenta que
# o proprio cron manda rodar para decidir.
S = json.load(open('Models/CALIBRATION_AND_VALIDATION/validation_store.json', encoding='utf-8'))
J = json.load(open('New_Theory/mapa_das_65_fora.json', encoding='utf-8'))
recs = {r.case_id: r for r in all_records()}
res = {c: CaseResult.from_dict(S[c]) for c in S if c in recs}
comp = [(recs[c], r) for c, r in res.items()
        if rh.caso_comparavel(recs[c].source, recs[c].case_id)]
# ⚠️ CONSERTO 2026-08-16: os pisos saem de TODOS os casos do store, nao so dos
# COMPARAVEIS. Ate aqui a linha filtrava por `caso_comparavel` e o script
# discordava da triagem canonica sobre a fila de trabalho.
#
# O motivo e' especifico e vale registrar: uma curva pode estar FORA DO CENSO
# **exatamente por ser a replica** de outra (`_CID_NAO_COMPARAVEL`) -- a
# `lu2024_M8_fig18_amp1p0` e' o mesmo ensaio da `fig20_T22Nm` publicado em duas
# figuras, e o proprio CLAUDE.md diz que ela "fica no STORE (o par e' o piso de
# digitalizacao) mas fora do censo". Filtrar por comparabilidade jogava fora o
# unico par que da piso ao `LU_2024` => piso None => a `fig20_T10Nm` caia em
# `indecidivel_sem_piso` (tem estatuto!) no script e em `form_limited` (fila de
# trabalho) na triagem. Zero contra um, sobre a MESMA curva.
#
# Canonico = o que decide o tripe: `report_html` chama `_pisos_medidos` sobre
# `records` inteiro nas duas linhas que julgam (L5354 e L6140); so um PAINEL
# usa o subconjunto comparavel.
#
# Licao (irma da que este arquivo ja carrega): chamar o mesmo helper NAO basta
# -- a POPULACAO passada a ele faz parte da regra. Dois instrumentos podem usar
# a funcao canonica e ainda assim discordar.
pisos = rh._pisos_medidos([(recs[c].source, r) for c, r in res.items()])


def passa(cid):
    """Regra canonica, pelo helper -- nunca reimplementada."""
    r = res.get(cid)
    if r is None:
        return None
    sd = rh.sres_para_censo(r)
    return (r.mae <= rh.META_MAE and r.maxerr <= rh.META_MAX
            and sd is not None and sd <= rh.limite_sres(recs[cid].source, pisos))


def vies(c):
    r = res[c]
    return float(np.mean(np.asarray(r.metric_pred, float)
                         - np.asarray(r.metric_data, float)))


G = defaultdict(lambda: dict(total=0, aberta=0, estat=0, pos=0, neg=0))
CAMADAS = defaultdict(int)
fechadas = []
for L in J:
    cid = L['cid']
    if cid not in res:
        continue
    if passa(cid):                       # fechou desde que o mapa foi escrito
        fechadas.append((cid, L['depende']))
        continue
    d = L['depende'] if L['depende'] != '-' else '(tem estatuto)'
    g = G[d]; g['total'] += 1
    # ⚠️ CONSERTO 2026-08-14: ate aqui a linha era
    #     tem = cid in rh._EXCECOES or cid in rh._DECLARADAS
    # ou seja, DUAS camadas de estatuto num sistema que hoje tem CINCO. As
    # curvas de `classe_parada` (8), `metric_limited` (1) e
    # `indecidivel_sem_piso` (15) caiam em "ABERTAS", e o script reportava 19
    # alvos onde a triagem canonica reporta ZERO form-limited. Quem lesse a
    # saida concluiria que ha 19 curvas acionaveis.
    #
    # E' o §4.43 num eixo que o cabecalho deste arquivo NAO previu: ele guarda
    # contra a lista de curvas envelhecer (re-mede pertinencia contra o store) e
    # nao contra o VOCABULARIO de estatuto envelhecer. Guardar contra uma forma
    # de envelhecimento nao guarda contra as outras.
    #
    # Agora pergunta ao classificador CANONICO da triagem — o mesmo que o cron
    # manda rodar — em vez de reimplementar a regra.
    camada = classificar(cid, S[cid], recs[cid].source,
                         piso_da_fonte(pisos, recs[cid].source),
                         set(rh._EXCECOES))
    CAMADAS[camada] += 1
    if camada != 'form_limited':
        g['estat'] += 1
    else:
        g['aberta'] += 1
        g['pos' if vies(cid) > 0 else 'neg'] += 1

print('CENSO POSSIVEL por proposta -- "curva fora" NAO e "ganho de censo"')
print()
print('%-16s %6s %11s %8s   %7s %7s' % ('decisao', 'fora', 'c/estatuto', 'ABERTAS', 'vies+', 'vies-'))
for k in sorted(G, key=lambda z: -G[z]['aberta']):
    g = G[k]
    print('%-16s %6d %11d %8d   %7d %7d' % (k, g['total'], g['estat'], g['aberta'], g['pos'], g['neg']))
print()
print('total fora %d  ·  com estatuto %d  ·  ABERTAS %d' % (
    sum(g['total'] for g in G.values()), sum(g['estat'] for g in G.values()),
    sum(g['aberta'] for g in G.values())))
print()
print('CAMADA DE ESTATUTO das que seguem fora — SOMENTE sobre as %d curvas do MAPA'
      % len(J))
print('CONGELADO (classificador canonico da triagem, denominador do MAPA):')
for k in sorted(CAMADAS, key=lambda z: -CAMADAS[z]):
    print('   %-34s %d' % (k, CAMADAS[k]))
print('   ⚠️ so `form_limited` e fila de trabalho; as demais tem procedencia.')
print('   ⚠️ ESTES NUMEROS NAO SAO O CENSO. O canonico e a')
print('      `regra_de_parada_triagem`, que roda sobre o STORE INTEIRO. Esta')
print('      decomposicao usa o denominador do mapa e por isso da MENOS —')
print('      comparar as duas lado a lado sem ler esta linha ja pareceu')
print('      divergencia de instrumento (medido 2026-08-15).')
if fechadas:
    print()
    print('FECHARAM desde o mapa (%d) -- saem da conta, e o mapa esta a re-gerar:' % len(fechadas))
    for cid, dep in fechadas:
        print('   %-40s (estava sob: %s)' % (cid, dep))

# ⚠️ O OUTRO SENTIDO (acrescentado 2026-08-15). Ate aqui o script reportava so
# as que FECHARAM desde o mapa — nunca as que estao fora HOJE e o mapa nao
# conhece. A assimetria mostrava progresso e escondia regressao/crescimento, e
# num relatorio de cobertura de proposta isso e' exatamente o vies errado.
# ⚠️ O filtro de COMPARABILIDADE tem de estar aqui tambem. Sem ele a secao
# lista as 3 `UFU_*` (fora do projeto desde 2026-08-01) e a duplicata
# `lu2024_fig18_amp1p0` (`_CID_NAO_COMPARAVEL`) — 10 em vez de 6, e as 4 a mais
# sao justamente as que NAO estao no censo. Erro cometido e corrigido na mesma
# escrita: o `res` do script inclui incomparaveis de proposito, e todo consumidor
# novo precisa re-aplicar `rh.caso_comparavel`.
_no_mapa = {L['cid'] for L in J}
_fora_hoje = sorted(c for c in res
                    if c not in _no_mapa and passa(c) is False
                    and rh.caso_comparavel(recs[c].source, c))
if _fora_hoje:
    print()
    print('FORA HOJE e AUSENTES DO MAPA (%d) -- nenhuma proposta as cobre, porque'
          % len(_fora_hoje))
    print('o mapa foi escrito antes delas existirem/cairem:')
    _cam_de = {cid: classificar(cid, S[cid], recs[cid].source,
                                piso_da_fonte(pisos, recs[cid].source),
                                set(rh._EXCECOES))
               for cid in _fora_hoje}
    for cid in _fora_hoje:
        print('   %-46s %s' % (cid, _cam_de[cid]))
    _fl = [c for c in _fora_hoje if _cam_de[c] == 'form_limited']
    print('   -> destas, %d sao `form_limited` (fila de trabalho REAL nao coberta)'
          % len(_fl))
print()
print('LEITURA: so as ABERTAS podem subir o censo. E dentro delas o SINAL do vies')
print('separa quem responde a uma forma que ADICIONA perda (vies+) de quem precisa')
print('do contrario (vies-). Foi isso que levou a P-14 de "12 alvo" a 4x5.')
