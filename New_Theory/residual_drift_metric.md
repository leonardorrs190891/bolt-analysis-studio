# Métrica de divergência — deriva do resíduo assinado (β), medida no store inteiro

**Data:** 2026-07-28 · **Pedido do professor:** *"o modelo pode estar divergindo e nem
sabemos… evitar modelos que acertam bem no começo e erram muito no final, e vice-versa"*
**Status:** INFORMACIONAL (medida, documentada; promoção a 4ª perna do tripé = prereg
assinado — regra da linha de métrica, §4.48a). **Custo:** pós-processamento puro dos
vetores `metric_x/pred/data` que o store já guarda (lição da banda v2: zero runner).

## 1. Por que σ_res não basta (e o professor está certo)

O tripé JÁ tem a 3ª perna σ_res — mas desvio-padrão é **permutação-invariante**:
embaralhar os resíduos no tempo não muda σ. "Acerta no começo, erra no final" é uma
propriedade de **ordem**, e nenhuma das três pernas a mede diretamente (o maxerr só
dispara quando o desvio passa de 0,10 em algum ponto; a classe escondida é a curva que
**deriva por baixo** disso). Medido: `corr(|β|, σ_res) = 0,686` nas 147 do tripé —
a ordem carrega informação que a dispersão não tem.

## 2. A métrica

Nos vetores da métrica (já alinhados e trimados — os MESMOS 3 vetores que o MAE usa):

- `e_i = pred_i − data_i` (resíduo **assinado**)
- `s_i = (x_i − x_0)/(x_fim − x_0)` ∈ [0,1]
- **β = slope de e vs s** (mínimos quadrados). Unidade: ratio por curva-inteira —
  β = +0,10 significa "o viés caminha uma tolerância inteira do começo ao fim".
  Sinal + = o modelo fica **otimista no fim** (retém mais que o dado); − = pessimista.
- `d3 = ⟨e⟩(último terço) − ⟨e⟩(primeiro terço)` — versão robusta, mesma leitura.

Nota técnica: o alinhamento (`align`) força e≈0 no 1º ponto, então β mede **taxa de
acumulação de viés** — exatamente "divergência". β e d3 concordam em sinal em todos
os flagados (tabela no JSON).

## 3. O que a varredura achou (store `294808504d83`, 202 casos com vetores)

| corte | curvas do tripé flagadas | leitura |
|---|---:|---|
| \|β\| > 0,05 (meia tolerância) | **36 / 147** | divergência escondida real e comum |
| \|β\| > 0,10 (tolerância inteira) | **4 / 147** | `chu test5` +0,136 · `karlsen run7p1` +0,114 · `jcsr galv_seawater` +0,108 · `eccles fig7d` −0,107 |

- Mediana de β nas 147: **−0,0005** — não há viés global; a deriva é por-curva.
- O `eccles fig7d` (β=−0,107) é o caso que o S4 já tinha tirado dos aprovados por
  artefato de FLOOR_TRIM — a deriva o pega **automaticamente**, o que é evidência de
  que a métrica mede o que promete.
- 1 caso sem vetores (`10_Yang_2023…below_threshold_7`, fora do batch-202? conferir)
  — fallback cru, não pontuado aqui.

## 4. Recomendação (em 3 degraus, do barato ao caro)

1. **AGORA (feito):** script + JSON como check informacional avulso
   (`residual_drift_metric.py`), rodável em qualquer store.
2. **Painel informacional** no report mestre (idioma do L7 `removal_energy_check`:
   nunca altera número de trajetória; colore a curva no report com β e d3) — follow-up
   de report, sem gate.
3. **Promoção a 4ª perna** (`|β| ≤ 0,05` como cláusula do tripé): é MUDANÇA DE MÉTRICA
   ⇒ exige prereg assinado do professor com contas de impacto: no corte 0,05 a meta
   cai **147→111** no ato (36 saem); no corte 0,10 cai 147→143. A alternativa honesta
   é usá-la como **critério de desempate/vigilância** (flag no report + item de fila
   por fonte flagada), não como porta.

## 5. Reprodutibilidade

```bash
py -3.12 New_Theory/residual_drift_metric.py   # ~5 s; só lê o store
```
Saída: `residual_drift_metric.json` (β, d3, σ, tripé, flag por curva).
