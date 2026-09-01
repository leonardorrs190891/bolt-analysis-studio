# Erro contra a CONDIÇÃO × erro contra a RÉPLICA — medido, 2026-08-23

**Pergunta do professor:** *"devemos poder discutir como o software lida com o erro para
situações de réplica no experimental que tem variação. Não ajustamos a curva do ensaio, e
sim a condição."*

Só-leitura. **Nada adotado** — mudança de métrica é decisão do professor. Store **`db7de97e682a`** (medido, não citado — peguei um estado transitório
`22f2e5631717` no meio da adoção da sessão paralela e o `CLAUDE.md` já avisa que
fingerprint de store envelhece mais rápido que número: **cite o censo, meça o
fingerprint**), censo **tripé 171/205**.

> ## ⚠️ A resposta INVERTEU no meio da medição, e o experimento foi natural
>
> Eu ia recomendar a leitura por condição como **porta** (pass/fail). Em 20 minutos o
> projeto produziu a contraprova sozinho, com **dado idêntico**. Está na §4, e é o achado
> mais importante deste documento.

---

## 1. A tese já está adotada — para UMA adoção, não para a métrica

A **adoção D-I** (CACCESE 45 kN, 2026-08-04) registra exatamente a tese do professor:

> *"os viesses do modelo contra as duas réplicas eram ambos negativos ⇒ o modelo estava
> abaixo das duas, fora da banda que o próprio dado não distingue. **Quando a condição tem
> réplicas, o alvo legítimo é o CENTRO delas; fitar contra uma é escolha arbitrária, e foi
> ela que produziu o defeito.**"*

A **métrica** nunca seguiu: ela pontua cada réplica contra o dado *daquela* réplica. As duas
correções existentes mexem no veredito sem mudar a **pergunta**:

| mecanismo | o que faz | natureza |
|---|---|---|
| **D1** (2026-07-30) | afrouxa o limite de σ da fonte para `max(0,025; piso medido)` | corrige a **barra**, por fonte |
| **F7 "prova de piso"** | desculpa a curva quando o erro ≤ piso da fonte | corrige o **veredito**, por curva |

## 2. A medição

15 condições com ≥2 réplicas, identificadas pela **chave estendida** adotada hoje (1º uso
dela para outra coisa), cobrindo **65 das 205** curvas. Comparação **pareada na mesma grade**
de 60 pontos da janela comum:

| condição | n | erro vs **condição** | erro vs réplica (médio) | razão | banda do dado | dentro? |
|---|---:|---:|---:|---:|---:|:--:|
| BAUER_2024 | 6 | 0,0586 | 0,0940 | 1,6× | 0,4587 | ✅ |
| BAUER_2024 | 3 | 0,0327 | 0,0511 | 1,6× | 0,3888 | ✅ |
| CACCESE_2009 | 2 | 0,0146 | 0,0351 | 2,4× | 0,0696 | ✅ |
| CHU_2026 | 2 | 0,0225 | 0,0407 | 1,8× | 0,0779 | ✅ |
| ECCLES_2010 | 4 | 0,0573 | 0,0784 | 1,4× | 0,1866 | ✅ |
| LIU_2016 | 2 | 0,0652 | 0,0655 | 1,0× | 0,0136 | ❌ |
| LIU_2017_AXIAL | 5 | 0,0181 | 0,0190 | 1,1× | 0,1510 | ✅ |
| LIU_2020_WEAR | 3 | 0,0313 | 0,0338 | 1,1× | 0,0121 | ❌ |
| LIU_2022_RETIGHT | 18 | 0,0033 | 0,0229 | **6,9×** | 0,1402 | ✅ |
| LIU_2025 | 2 | 0,0718 | 0,0721 | 1,0× | 0,0428 | ❌ |
| LI_2022_TRIBOINT | 2 | 0,0574 | 0,0575 | 1,0× | 0,0610 | ✅ |
| LU_2024 | 2 | 0,0753 | 0,0755 | 1,0× | 0,0162 | ❌ |
| YANG_2021 | 3 | 0,0327 | 0,0573 | 1,8× | 0,0660 | ✅ |
| ZHANG_2018 | 7 | 0,0317 | 0,0349 | 1,1× | 0,0212 | ❌ |
| ZHANG_2019 | 4 | 0,0195 | 0,0244 | 1,2× | 0,0359 | ✅ |

**O modelo está dentro da banda que o dado não resolve em 10 das 15.** E o erro contra a
réplica é **sempre ≥** o erro contra a condição.

**Se a leitura por condição fosse porta, 7 curvas hoje reprovadas passariam** (BAUER ×5,
YANG_2021 ×1, ZHANG_2019 ×1). O `LIU_2025` reprova nos **dois** níveis ⇒ a leitura
**discrimina, não absolve**.

## 3. O achado que sobrevive a tudo: a BANDA diz onde o dado consegue decidir

As 5 condições em que o modelo está **fora** da banda são justamente as de banda **estreita**
(0,0121–0,0428): dado bom, modelo errado — **trabalho real**. As de banda larga
(BAUER 0,459 e 0,389!) são aquelas em que o experimento não se repete o suficiente para
julgar.

⇒ **Banda estreita + modelo fora = defeito. Banda larga + modelo dentro = o dado não sabe
responder. A métrica de hoje não distingue as duas.** Isto vale independentemente de
qualquer decisão sobre porta ou censo.

## 4. ⚠️ A INVERSÃO — experimento natural, mesmo dia, dado idêntico

Às 20:0x retratei as 2 provas de piso do ECCLES (o denominador estava inflado por contagem
dupla). Contra a **condição**, o res.máx era **0,0851** — dentro da meta de 0,10. Eu ia
escrever: *"a retratação foi desnecessária; a leitura por condição as aprovaria"*.

Às 20:4x a sessão paralela, **porque as duas voltaram para a fila**, achou a rota
`arrest_approach_exp` por protocolo e adotou. Resultado, **com o dado exatamente igual**:

| | antes | depois | banda do dado |
|---|---:|---:|---:|
| `fig8a` res.máx individual | 0,1320 | **0,0488** | — |
| `fig8c` res.máx individual | 0,1463 | **0,0708** | — |
| erro vs **condição** | 0,0851 | **0,0573** | — |
| erro vs réplica (médio) | 0,1045 | **0,0784** | — |
| **diferença entre as duas leituras** | **0,0603** | **0,0211** | **0,1866 (inalterada)** |

**As duas curvas passam o tripé por mérito** — sem exceção, sem leitura alternativa.

### Duas consequências, e as duas mudam a proposta

**(a) A diferença entre as leituras NÃO é o espalhamento do dado.** Eu havia escrito que era.
Medido: ela caiu **3×** sem o dado mudar um ponto. Logo o erro por réplica cobra do modelo
**duas** coisas — o espalhamento da réplica (ilegítimo) **e** o erro de forma do próprio
modelo interagindo com esse espalhamento (legítimo). **Uma medição isolada não separa as
duas**; só um par antes/depois separa, e é por isso que a leitura por condição não pode ser
porta.

**(b) Como PORTA, ela teria custado a melhoria.** Se eu a tivesse adotado às 20:1x, as duas
curvas "passariam" em 0,0851 e **ninguém procuraria o `arrest_approach_exp`** — que rendeu
**2,7× no res.máx**. A pressão que produziu física nova veio de elas estarem na fila.

É o precedente **D-M**, agora com segunda instância: *"recusar declarar-para-desbloquear
forçou a medição que deu o resultado MELHOR"*. E vale registrar o que isso diz da retratação
de hoje: ela **não** foi custo — foi o que colocou as curvas onde alguém as consertaria.

## 5. Proposta REVISADA (NÃO executada)

**Como DIAGNÓSTICO publicado, não como porta:**

1. A métrica por curva **segue sendo a única porta**. É ela que compara com o artigo, e é
   ela que mantém a pressão que produz física.
2. Publicar, ao lado dela, para as 15 condições com réplica: **erro contra a condição**,
   **banda do dado** e a **razão** entre as duas leituras. Isso responde à pergunta do
   professor sem trocar a régua.
3. **Usar a razão como triagem de esforço**, que é o valor prático: razão ≈ 1,0 com modelo
   fora da banda estreita (`LIU_2016`, `LU_2024`, `LIU_2025`) = defeito de forma, ataque
   direto. Razão alta com banda larga (`BAUER` 1,6× em banda 0,46) = o experimento é o
   limitante, e nenhuma forma nova resolve.
4. **A F7 fica como está.** A leitura por condição seria um substituto mais principiado *se*
   fosse porta — e a §4 mostra que não deve ser.

**O que continua sendo sua decisão:** (a) publicar o diagnóstico no report mestre, no por
caso, ou só aqui? (b) a razão entra como 4ª coluna da triagem de esforço? (c) vale reabrir a
questão de porta se aparecer uma 2ª instância em que a leitura por condição aprove curva que
**nenhuma** física conhecida fecha?

## 6. Riscos medidos

**(a) Média mascara erro de sinal oposto:** real, **1 das 15** (`LIU_2022_RETIGHT`, 6,9× —
cadeia de 18 estágios, onde a média sobre 18 esconde erro por estágio). Nas outras 14 a
razão é ≤ 2,4×. Guarda proposta se algum dia virar porta: razão ≤ 3.

**(b) Cobre 65 de 205.** As outras 140 não têm réplica ⇒ como diagnóstico é assimetria
aceitável; como porta criaria duas classes de curva.

**(c) "Centro" de 2 réplicas é estimador fraco** — 9 das 15 têm n=2 ou 3.

## 7. Errata do meu próprio instrumento

**(a)** Eu ia publicar *"o modelo dá previsões diferentes para a mesma condição em 13 de 15 ⇒
assinatura fit-like"*. **Retirado**: o `disp_MODELO` tem três causas e não separa fit de
condição —

| causa | famílias | é fit? |
|---|---:|---|
| `n_max` difere ⇒ amostragem em grade de ~400 pts | 11 | **não, é o instrumento** |
| `align` difere (1º ciclo do dado: YANG 18/20/500) | 2 | não, normalização legítima |
| `overrides` diferem ⇒ constante por curva | 7 | **sim** |

O gotcha do projeto já registra que interpolar na grade **amostrada** erra até 46 % no
transiente.

**(b)** Rotulei uma coluna de `initial_preload_N` como *"F₀ alcançado"* quando ela é o
**registrado** — o alcançado vive no 1º ponto da CSV.

**(c)** Escrevi que a diferença entre as leituras *é* o espalhamento do dado (§4a).

Três leituras de instrumento fora do domínio nesta medição; as três pegas antes de publicar.
A comparação da §2 sobrevive porque é **pareada na mesma grade** — o artefato de amostragem
afeta os dois lados igualmente, e o que se lê é a **diferença**.

## 8. Reprodutibilidade

```bash
py -3.12 New_Theory/condicao_vs_curva.py     # gera condicao_vs_curva.json
```

Famílias pela chave de `_pisos_medidos` (`_CAMPOS_VARRIDOS`); vetores de
`metric_x`/`metric_data`/`metric_pred`, nunca reinterpolados da curva crua.
