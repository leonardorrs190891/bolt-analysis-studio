# Proposta **F8**: a fila "form-limited" tem 2 curvas e **nenhuma delas é de forma**

> # ⛔ **RETIRADA POR MIM, 40 MINUTOS DEPOIS DE PROPOSTA — o piso não é de réplica**
>
> **Não assine esta proposta.** Ao atacar a curva que ela *não* propunha
> (`amp1p0_long`), medi as curvas do par e descobri que **os pares declarados do `LU_2024`
> não se comportam como réplicas**. O piso que sustenta o F7 desta proposta mede outra
> coisa.
>
> **A medida que decide — tempo até o dado cair de F/F₀ = 0,90:**
>
> | par (mesma condição nominal) | `fig14` | `fig18/20` | razão |
> |---|---:|---:|---:|
> | 0,25 mm | **27** ciclos | **1** | 27× |
> | 0,5 mm | **27** | **1** | 27× |
> | 1,0 mm | **56** | **1** | 56× |
>
> **Três pares, três vezes, mesma direção.** Dispersão de réplica **espalha** — às vezes um
> lado segura, às vezes o outro. Sistemático 3/3 com fator 27–56× é **diferença entre as
> figuras**, não repetibilidade do ensaio.
>
> Sinal independente na mesma direção: as janelas não batem —
> `fig14_amp0p25_long` vai a **N = 1040** e `fig18_amp0p25` a **N = 99**. São **durações
> diferentes**; o `x_offset` (0 na fig14, 1 na fig18/20) desloca **1 ciclo**, não 27.
>
> ⇒ o piso não mede *"o quanto duas medições da mesma condição discordam"*; mede **o quanto
> a Fig. 14 difere das Figs. 18/20**. Um F7 construído sobre ele demonstra que o modelo
> erra menos que essa diferença — o que **não é** a afirmação que a exceção precisa fazer.
>
> **Por que retiro em vez de emendar:** é a terceira vez que esta campanha encontra piso
> inválido por pareamento (`_EXCECOES_RETRATADAS_LU_PISO_INVALIDO`,
> `_EXCECOES_RETRATADAS_ROUSSEAU_PISO_INVALIDO`), e nas duas anteriores a lição foi a
> mesma: **validade do par vem antes do número**. Eu tinha a lição escrita e ainda assim
> propus — o que a torna registro, não conhecimento.
>
> **A medição da proposta continua correta e útil** (o erro do modelo *é* 48–70 % daquele
> piso); o que caiu foi a **interpretação** do piso. O texto original segue intacto abaixo.
>
> ⚠️ **Consequência que NÃO é minha para resolver:** **5 exceções assinadas do `LU_2024`**
> (`fig18_amp0p5`, `fig20_T10Nm`, `T16Nm`, `T22Nm`, `T28Nm`) repousam sobre **estes mesmos
> pisos**. Não as retrato — foram assinadas pelo professor e a decisão é dele. Estão
> listadas, com os números, em `lu2024_pares_declarados_nao_sao_replicas.md`.

**2026-08-14** · só-leitura · **nada adotado** · store `55273eab12b0`, censo **147/205** ·
⚠️ **exige assinatura** (reclassificação de camada).

## O que motivou medir

A triagem chama `form_limited` de *"o único alvo legítimo"*, e ela está em **2 curvas**,
ambas `lu2024_M8_fig14_*_long`. Antes de desenhar qualquer forma nova para elas — que é o
trabalho caro e o que está fora do mandato autônomo —, a pergunta barata:

> **O erro do modelo nessas 2 é maior ou menor que a discordância entre duas medições da
> própria condição?**

Se for menor, o rótulo está errado: não falta forma, falta **dado com menos dispersão**.

## A régua: pares de réplica DECLARADOS, com procedência

Cada uma tem par de réplica **da própria condição nominal**, declarado em prereg
(`2026-07-31-pares-replica-declarados`) com proveniência — não é a chave mecânica cega que
esta campanha já teve de retratar duas vezes:

| curva | par declarado |
|---|---|
| `fig14_amp0p5_long` | ↔ `fig18_amp0p5` — *"22 N·m / 0,5 mm — §3.1.3 × Fig. 18"* |
| `fig14_amp1p0_long` | ↔ `fig20_T22Nm` — *"22 N·m / 1,0 mm — §3.1.3 × Fig. 20"* |

Critério F7 vigente: **FORTE** = erro ≤ piso/√2 (a barra de *"tão bom quanto o centro das
réplicas"*); **PROVA** = erro ≤ piso. A prova exige **todas** as pernas violadas cobertas —
foi por não exigir isso que 2 assinaturas foram retratadas em 2026-07-31
(`_EXCECOES_RETRATADAS_F7_PERNA_DESCOBERTA`).

## ✅ `lu2024_M8_fig14_amp0p5_long` — **F7 FORTE nas 3 pernas**

| perna | modelo | piso | piso/√2 | % do piso | veredito |
|---|---:|---:|---:|---:|---|
| MAE | **0,1257** | 0,2630 | 0,1860 | **48 %** | **FORTE** |
| res.máx | **0,3936** | 0,5780 | 0,4087 | **68 %** | **FORTE** |
| σ_res | **0,1235** | 0,1768 | 0,1250 | **70 %** | **FORTE** |

⇒ o modelo está **mais perto desta curva do que a réplica da mesma condição está**, nas três
pernas. Chamar isso de *"limitado por forma"* inverte o diagnóstico: **nenhuma forma nova
pode ser validada aqui**, porque o instrumento de validação (o dado) não resolve diferenças
desse tamanho.

⚠️ **Margem fina numa perna, dita antes que alguém a descubra:** o σ passa por **1,2 %**
(0,1235 contra 0,1250). Se o piso for re-medido e cair 2 %, esta perna vira PROVA em vez de
FORTE — o que **não** anula a exceção (PROVA é classe válida), mas muda o rótulo. As outras
duas têm folga confortável (48 % e 68 %).

## ⛔ `lu2024_M8_fig14_amp1p0_long` — **NÃO elegível**, e por pouco

| perna | modelo | piso | % do piso | veredito |
|---|---:|---:|---:|---|
| MAE | 0,4802 | 0,5187 | 93 % | PROVA |
| **res.máx** | **0,8553** | **0,8498** | **101 %** | ⛔ **DESCOBERTA** |
| σ_res | 0,2894 | 0,3044 | 95 % | PROVA |

O res.máx está **acima** do piso — por **0,65 %**. Duas pernas cobertas não fazem exceção; a
regra exige **todas**. Registro isto explicitamente porque a tentação de arredondar 101 %
para "dentro" é exatamente o mecanismo que produziu as retratações de 2026-07-31, e a regra
existe para valer **contra** quem a invoca.

**Ela continua na fila**, e agora com diagnóstico melhor: não é "forma faltante" genérica, é
uma curva cujo **erro de pico** excede o scatter enquanto nível e dispersão não excedem —
assinatura de **um evento localizado** mal reproduzido, não de taxa errada ao longo do
ensaio.

## O que isto muda no censo, se assinado

| leitura | hoje | com F8 |
|---|---:|---:|
| tripé estrito | 147 | 147 (inalterado — exceção não fecha curva) |
| resolvidas (tripé + exceção assinada) | 168 | **169** |
| **fila form-limited** | **2** | **1** |

⚠️ **Exceção retira da meta, não fecha curva** — a leitura estrita segue 147/205, e é assim
que deve ser publicado. O ganho real é de **diagnóstico**: a fila do professor deixa de
conter uma curva que nenhuma forma pode consertar.

## Caveat honesto sobre a construção F7

O piso é `|A − B|` entre as duas réplicas, e o erro é `|modelo − A|` — com **A dentro do
par**. O modelo foi calibrado nesta fonte, então "bater o piso" não é predição cega. É a
mesma construção sob a qual as **32 FORTE + 6 PROVA** já assinadas foram aceitas, e o que ela
demonstra é bem definido: *o erro do modelo é menor que a incerteza com que o dado define a
própria condição* — o que basta para concluir que **melhorar o modelo aqui é inverificável**,
que é a única afirmação que a exceção faz.

## Decisão do professor

1. **Assinar a F8** para a `amp0p5_long` (FORTE 3/3) ⇒ fila legítima cai de 2 para 1; ou
2. **Recusar** e mantê-la como form-limited — o que exigiria explicar como validar uma forma
   nova contra um dado cuja dispersão é 2× o erro atual; ou
3. **Re-medir o piso** antes de decidir (a margem de 1,2 % no σ é o único ponto fino).

A `amp1p0_long` **não está sendo proposta** — ela reprova pelo meu próprio gate.

## Reprodutibilidade

Pisos por `report_html._pisos_medidos` (pares declarados incluídos); métricas do store
`55273eab12b0`; veredito F7 pelos limiares vigentes (piso/√2 e piso). Segundos, só-leitura.
