# Qualificar o software: o que falta, medido — 2026-08-25

**Pergunta do professor:** *"que outras curvas e gráficos sugere para qualificar o
software?"*

Só-leitura. Censo **171/205**, fingerprint `db7de97e682a`.

---

## O enquadramento, e por que ele muda a lista

O projeto tem **validação** farta — 205 curvas, tripé por curva, piso por fonte, exceções
com prova, 38 falsificações registradas. O que quase não existe é o **outro lado da
qualificação**: *verificação* (as equações estão sendo resolvidas certo?) e *aptidão para a
decisão* (o software responde certo a pergunta que o engenheiro faz?).

⇒ As sugestões abaixo não são "mais gráficos de curva". São os eixos que faltam.

---

## ⚠️ 1. Matriz de decisão ISO/DIN — a mais importante, e a que expõe um risco real

**Medido agora**, sobre as 205 comparáveis, no ponto final de cada curva:

| norma | limiar | acerto | falso **alarme** | falso **SEGURO** |
|---|---|---:|---:|---:|
| ISO 16130 | reter ≥ 85 % | **94,1 %** | 5 | **7** |
| DIN 25201-4 | reter ≥ 80 % | **95,6 %** | 3 | **6** |

**Falso seguro** = o modelo diz *"a junta retém"* e o dado diz que afrouxou. É o único erro
com consequência de engenharia, e o projeto **nunca publicou este número**.

⚠️ **E o achado que justifica a página inteira: 3 dos 7 falsos seguros PASSAM o tripé.**

| curva | dado | modelo | MAE | no tripé? |
|---|---:|---:|---:|:--:|
| `rousseau2025_hdpe_t10_amp0p2` | 0,799 | **0,869** | 0,0260 | **SIM** |
| `liu2022_fig8_multi_t4` | 0,845 | **0,924** | 0,0380 | **SIM** |
| `sun2025efa109235_axial_F17.5kN_standard` | 0,814 | **0,861** | 0,0330 | **SIM** |
| `yang2021_fig2_typical` | 0,786 | 0,948 | 0,0404 | não |
| `yang2021_amp1p0mm_ax2kN` | 0,807 | 0,915 | 0,0285 | não |
| `yang2021_amp0p8mm_ax6kN` | 0,772 | 0,946 | 0,0542 | não |
| `10_Yang_2023 … 0,25 mm` | 0,520 | 0,946 | 0,1664 | não |

A primeira tem **MAE 0,0260** — fidelidade excelente — e mesmo assim informaria *"87 % de
retenção"* onde o ensaio mede **80 %**. **O tripé mede fidelidade de curva; ele não mede
acerto de decisão, e os dois discordam.** Isso não é defeito do tripé: é uma pergunta que
ele não faz.

**O gráfico:** matriz de confusão nos dois limiares, com as curvas do quadrante perigoso
**nomeadas** e ligadas à página do artigo. Custo: baixo — os números estão acima.

## 2. Diagrama de paridade — o gráfico canônico de V&V que falta

**Medido:** previsto × observado no ponto final das 205 curvas.

| | |
|---|---:|
| R² contra a reta 1:1 | **0,9455** |
| viés médio | **+0,0083** |
| \|viés\| mediano | 0,0252 |
| dentro de ±0,05 | **78 %** |
| dentro de ±0,10 | **93 %** |

O viés **positivo** diz que o modelo, na média, **retém mais** que o dado — o que é
coerente com os 7 falsos seguros contra 5 falsos alarmes. Um gráfico, duas leituras.

**O gráfico:** paridade com a reta 1:1, banda de ±0,05/±0,10, cor por fonte e o quadrante
de falso seguro sombreado. Custo: baixo.

## 3. Mapa de cobertura — onde o software interpola e onde extrapola

**Medido:** a faixa que o corpus cobre.

| variável | n | faixa | mediana |
|---|---:|---|---:|
| amplitude [mm] | 150 | 0,04 – 2,0 | 0,30 |
| F₀ [kN] | 205 | 2,1 – 720 | 18 |
| diâmetro [mm] | 205 | 6 – 42 | 12 |
| frequência [Hz] | 205 | 1,2·10⁻⁵ – 30 | 10 |

As faixas são largas, mas **ninguém sabe onde estão os buracos**. Um usuário que rodar um
M20 a 0,8 mm e 5 Hz não tem como saber se está dentro do envelope validado.

**O gráfico:** projeções 2D do espaço (amplitude × F₀, diâmetro × frequência) com um ponto
por curva e as regiões vazias visíveis. É o que transforma *"validado em 205 curvas"* em
*"validado NESTE envelope"*. Custo: baixo.

## 4. Conservação de energia por caso — a lacuna de VERIFICAÇÃO

O engine calcula `analyzer.energy.conservation_residual`, e o `MODEL_MATH_REFERENCE`
afirma que ele é ≈ 0. **Medido: o store NÃO grava esse valor.** Ou seja, a afirmação
central de verificação do modelo não é auditável no corpus.

O que **está** gravado é o L7 (energia de remoção por wear): **130 curvas com valor, 48
dentro da banda de literatura, 82 fora** — até ~120× o teto de Shipway. A página não mostra.

**O gráfico:** residual de conservação por curva (histograma + pior caso), e o L7 contra a
banda 1800–10500 J/mm³. Custo: **médio** — exige gravar o residual no store, o que é um
campo novo e uma re-simulação.

## 5. Convergência / independência de passo — a outra lacuna de verificação

O engine integra **um ciclo por passo**. Ninguém demonstrou que a resposta é independente
disso: se rodar de 2 em 2 ciclos, ou de 10 em 10, a curva muda? Se muda, parte do resultado
é o passo, não a física.

**O gráfico:** curva de refinamento — erro contra o passo, em log-log, com a ordem de
convergência aparente. É o gráfico mais padrão de verificação de código que existe, e o
projeto não tem nenhum. Custo: **médio** (exige rodar com passo variado; pode ser em 5–10
curvas representativas, não nas 205).

## 6. Held-out sistemático — a claim de predição, com número

Existem casos zero-refit registrados (o ROUSSEAU HDPE previu condição inédita), mas não há
um estudo sistemático. E existe maquinaria: o commit `8336437` criou o split
leitura/held-out mecânico.

**O gráfico:** para cada fonte, o erro nas curvas usadas para calibrar × o erro nas
retidas. Se as duas nuvens coincidem, é predição; se separam, é ajuste. **Este é o gráfico
que responde "modelo ou fit" com um número em vez de argumento.** Custo: **alto** — exige
re-fitar por fonte.

## 7. Intervalo de predição com cobertura medida

Hoje o software dá um ponto. Qualificação pede banda. Da distribuição dos resíduos dá para
construir um intervalo de 90 % e então **medir a cobertura real** — se 90 % dos pontos caem
dentro, o intervalo é honesto; se caem 70 %, ele é otimista.

**O gráfico:** cobertura nominal × cobertura empírica. Custo: baixo (os resíduos existem).

## 8. Diagnóstico de resíduo, o pacote clássico

Q-Q dos resíduos, resíduo × valor ajustado, e autocorrelação ao longo do ciclo. O projeto já
mediu que **63 % dos resíduos trocam de sinal** e que o defeito é *curvatura, não taxa* — os
três gráficos mostram isso de relance e dizem se o resíduo é ruído ou estrutura remanescente.
Custo: baixo.

---

## Recomendação, em ordem

| # | gráfico | o que qualifica | custo | já mensurável? |
|---|---|---|---|---|
| **1** | **matriz de decisão ISO/DIN** | aptidão para a decisão | baixo | ✅ **medido acima** |
| **2** | **paridade** | acurácia global e viés | baixo | ✅ **medido acima** |
| **3** | **cobertura do espaço** | envelope de validade | baixo | ✅ **medido acima** |
| 7 | intervalo de predição | incerteza | baixo | ✅ resíduos existem |
| 8 | diagnóstico de resíduo | estrutura remanescente | baixo | ✅ |
| 4 | conservação de energia | **verificação** | médio | ⚠️ campo novo no store |
| 5 | convergência de passo | **verificação** | médio | ⚠️ exige re-simular |
| 6 | held-out sistemático | predição vs ajuste | alto | ⚠️ exige re-fit |

**Os três primeiros foram construídos** — `metodologia/qualificacao.html`. Os demais são
proposta, com o custo declarado.

⚠️ **A ordem não é por facilidade — é por consequência.** O #1 está em primeiro porque é o
único que mede o que o engenheiro **usa**, e porque a medição já mostrou que ele discorda do
tripé em 3 curvas aprovadas. Um software pode ter MAE excelente e mesmo assim informar
"seguro" onde o ensaio diz o contrário; nenhum dos gráficos existentes hoje mostraria isso.
