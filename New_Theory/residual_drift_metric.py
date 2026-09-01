"""Metrica de DIVERGENCIA (deriva do residuo) — pedido do professor 2026-07-28.

Pergunta: "o modelo pode estar divergindo e nem sabemos" — modelos que acertam
bem no comeco e erram muito no final (e vice-versa) escapam de metricas de
dispersao?

Fatos de partida:
- O tripe JA tem a 3a perna sigma_res (std dos residuos) — mas sigma e
  PERMUTACAO-INVARIANTE: nao distingue erro que CRESCE de erro que oscila.
  A informacao que falta e a ORDEM.
- maxerr pega estouro >=0,10 em qualquer ponto; a classe escondida e a curva
  que passa o tripe DERIVANDO por baixo de 0,10.
- Licao da banda v2 (4.48): antes de tocar o runner, verificar se a metrica
  e computavel dos vetores que o store ja guarda. E: metric_x/pred/data.

Metrica proposta (informacional; promocao a 4a perna = prereg do professor):
  e_i    = pred_i - data_i (residuo ASSINADO nas abscissas da metrica)
  s_i    = (x_i - x_0)/(x_end - x_0)  em [0,1]
  beta   = slope de e vs s (minimos quadrados)  [unidades de ratio por
           curva-inteira: beta=0,10 = o erro caminha uma tolerancia inteira
           do comeco ao fim]
  d3     = mean(e no ultimo terco) - mean(e no primeiro terco)  (robusto,
           mesma unidade; sinal + = fica pessimista/superpreve no fim)
  Nota: o alinhamento (align) forca e~0 no 1o ponto — beta mede TAXA DE
  ACUMULACAO de vies, que e exatamente "divergencia".

Flag de divergencia escondida: passa o tripe E |beta| > 0,05 (meia tolerancia).
"""
import sys, json, pathlib
import numpy as np
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

STORE = pathlib.Path('Models/CALIBRATION_AND_VALIDATION/validation_store.json')
store = json.loads(STORE.read_text(encoding='utf-8'))
P = print

out = {}
sem_vetores = []
for cid, s in store.items():
    if not isinstance(s, dict) or 'mae' not in s:
        continue
    x = s.get('metric_x'); pr = s.get('metric_pred'); da = s.get('metric_data')
    if not x or not pr or not da or len(x) < 5:
        sem_vetores.append(cid)
        continue
    x = np.asarray(x, float); e = np.asarray(pr, float) - np.asarray(da, float)
    span = max(x[-1] - x[0], 1e-9)
    si = (x - x[0]) / span
    beta = float(np.polyfit(si, e, 1)[0])
    n3 = max(len(e) // 3, 2)
    d3 = float(e[-n3:].mean() - e[:n3].mean())
    tripe = bool(s['mae'] <= 0.10 and s['maxerr'] < 0.10)
    out[cid] = dict(beta=beta, d3=d3, mae=s['mae'], maxerr=s['maxerr'],
                    sigma=float(np.std(e)), tripe=tripe,
                    escondida=bool(tripe and abs(beta) > 0.05))

P('curvas com vetores: %d | sem vetores (fallback cru): %d' % (len(out), len(sem_vetores)))
if sem_vetores:
    P('  sem vetores: %s' % ', '.join(sem_vetores[:6]) + (' ...' if len(sem_vetores) > 6 else ''))
tripe_ok = {c: v for c, v in out.items() if v['tripe']}
esc = {c: v for c, v in out.items() if v['escondida']}
P('')
P('no tripe: %d | DIVERGENCIA ESCONDIDA (tripe + |beta|>0,05): %d' % (len(tripe_ok), len(esc)))
P('')
P('%-46s %8s %8s %7s %7s' % ('curva (escondidas, por |beta|)', 'beta', 'd3', 'mae', 'maxerr'))
for c, v in sorted(esc.items(), key=lambda kv: -abs(kv[1]['beta'])):
    P('%-46s %+8.3f %+8.3f %7.3f %7.3f' % (c[:46], v['beta'], v['d3'], v['mae'], v['maxerr']))
P('')
# distribuicao geral do beta nas curvas do tripe
bs = np.array([v['beta'] for v in tripe_ok.values()])
P('beta nas %d do tripe: mediana %+0.4f | p90(|beta|) %.4f | max(|beta|) %.4f'
  % (len(bs), float(np.median(bs)), float(np.percentile(np.abs(bs), 90)),
     float(np.abs(bs).max())))
# sanity: correlacao |beta| x sigma (quanta informacao NOVA a ordem traz?)
sg = np.array([v['sigma'] for v in tripe_ok.values()])
r = float(np.corrcoef(np.abs(bs), sg)[0, 1])
P('corr(|beta|, sigma_res) nas do tripe: %.3f  (<1 = a ordem traz informacao nova)' % r)
json.dump(out, open('New_Theory/residual_drift_metric.json', 'w'), indent=1)
P('-> New_Theory/residual_drift_metric.json')
