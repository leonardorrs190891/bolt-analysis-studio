# Fase 4 — a regra de parada, MEDIDA contra o estado de hoje

**2026-08-16 (noite)** · store `7a60cacb72de`, censo **144/205** · só-leitura ·
regra: `New_Theory/regra_de_parada_proposta.md` · plano:
`New_Theory/plano_das_21_abertas.md`.

> **Resumo:** aplicada a cada classe presente na fila julgável, **os três
> critérios estão satisfeitos**. Mas o veredito vem com uma ressalva que muda a
> decisão: **duas curvas estão a 7–8 % de fechar**, e ambas estão numa classe
> que a campanha já declarou encerrada. Parar ou reabrir por essas duas é
> decisão sua, não medição minha.

## 1. Primeiro, o que a Fase 1 mudou na própria fila

A regra trata as curvas sem piso medido assim: *"as 15 sem piso ficam **fora da
fila** e fora das declaradas — rótulo `indecidível`, com a ação nomeada (uma
réplica na mesma condição por fonte)"*.

A Fase 1 (`piso_impossivel_nas_5_fontes.md`) **confirmou que essa ação nomeada é
a única disponível**: nas 5 fontes não existe par válido — 4 pares do ICMEZ
diferem no grip, o par do ROUSSEAU difere na espessura, os 8 do SUN cruzam
tratamento, e `YANG_2023`/`YANG_2019` não têm par nenhum.

⇒ **a fila julgável de hoje é de 6 curvas**, não 21.

## 2. Os três critérios, medidos

### (a) classe identificada por ≥2 instrumentos independentes — **SATISFEITO**

As 6 têm forma nomeada com documento. A `lu2024_fig20_T10Nm`, a mais distante,
tem dois instrumentos independentes: a varredura de torque da própria fonte
(excesso de perda no 1º ciclo ∝ 1/F₀ a **r = +0,995**) e um **controle negativo
que passa** (no `CACCESE_2009`, onde o embedding carrega 0,2 % da perda, o sinal
desaparece).

### (b) todo membro da classe falsificado por predição pré-registrada — **SATISFEITO nas classes presentes**

| curva | classe | estado |
|---|---|---|
| `lu2024_fig20_T10Nm` | encaixe cego à pré-carga **+** piso terminal | `emb_pressure_exp` construído e **falsificado pelo G1** (16/08); o piso fecha por argumento **estrutural** — fração única de F₀ não gera terminal não-monótono, e o dado é não-monótono e publicado |
| `yang2021` ×3, `liu2025` ×2 | "aceleração tardia" | classe **encerrada** em 2026-08-02 por 3 falsificações com prereg |

⚠️ **Ressalva de escopo, e ela é real:** a regra foi escrita para **uma** classe
("taxa dependente do estado acumulado"), e ali dois membros seguem sem sondagem
(bifurcação de limiar; o Cattaneo-Mindlin ficou **inconclusivo**, que a própria
regra diz não contar). **Nenhuma das 6 curvas de hoje pertence a essa classe** —
mas estender a regra de "uma classe" para "a campanha" é decisão, não medição.

### (c) retorno marginal medido e nulo — **SATISFEITO, e por construção**

Os quatro candidatos mais recentes, todos com prereg e gates congelados:

| candidato | data | desfecho |
|---|---|---|
| `emb_pressure_exp` | 16/08 | **falsificado** (G1: 3,2× o limite) |
| piso do `YANG_2023` | 16/08 | **premissa falsificada** antes de executar |
| `loose_arrest_residual` | 15/08 | **falsificado** (G2/G3) |
| `k_ratchet` no ROUSSEAU | 15/08 | **falsificado** (10 células) |

**(i) zero saídas por mérito de modelo.** Os ganhos de censo do período vieram de
**dado** (pico espúrio no LU) e de **procedência** (par de réplica do ECCLES) —
nenhum de forma nova.

**(ii) a mediana da distância caiu 0 %**, e isso não é estimativa: **nenhum dos
quatro foi adotado**, logo nenhuma métrica de nenhuma curva mudou por causa
deles. 0 % < 3 %.

## 3. ⚠️ O que a medição põe CONTRA parar

Distância ao limite, fila julgável:

| curva | pior perna | falta |
|---|---:|---:|
| `yang2021_amp0p6mm_ax8kN_r1` | 1,07× | **7,3 %** |
| `liu2025_M16_fig2_single` | 1,08× | **7,9 %** |
| `yang2021_amp1p0mm_ax2kN` | 1,28× | 28,0 % |
| `yang2021_amp0p5mm_ax8kN` | 1,55× | 55,0 % |
| `liu2025_M16_amp0p8` | 1,68× | 67,6 % |
| `lu2024_M8_fig20_T10Nm` | 5,03× | 402,8 % |

**Mediana: 41,5 %.**

As duas primeiras precisam de **7 % de redução no σ_res** para fechar — e as
duas estão em `classe_parada`. É o ponto exato da decisão: a campanha declarou
a classe encerrada por três falsificações, e agora duas curvas dessa classe
estão a menos de 8 % da barra.

**Não recomendo reabrir a classe por elas**, e o motivo é medido, não
conservadorismo: o σ delas é **2,6× e 1,8×** o ruído do próprio dado da fonte
(pisos 0,0103 e 0,0149). Fechá-las exigiria o modelo ficar mais próximo do dado
do que o dado fica de si mesmo em quase um fator dois — e a classe que
produziria isso é justamente a que foi falsificada três vezes.

Mas a distância é pequena o bastante para que a decisão seja sua.

## 4. Veredito

**A regra dispara** para a fila julgável de hoje. O que ela significa está
escrito na própria regra: a parada é **provisória** e **reabre automaticamente**
se o `engine_fingerprint` mudar, se um instrumento novo mudar a decomposição, se
`n` ou piso de qualquer curva mudar, ou se a régua mudar.

**O que isso NÃO é:** não é "o modelo está pronto", nem "as 61 fora estão
resolvidas". É a afirmação mais estreita e mais defensável que os dados
sustentam — **o modelo está no limite do que este corpus consegue julgar**:

- **6 curvas**: o modelo erra de verdade, com forma nomeada e rota fechada.
- **15 curvas**: falta dado para saber se erra.
- **40 curvas**: têm estatuto assinado (23 exceções, 17 declaradas).

## 5. A decisão que fica na sua mesa

1. **Aceitar a parada** para a fila julgável, com a reabertura automática já
   escrita na regra.
2. **Reabrir a `classe_parada`** pelas duas curvas a 7–8 % — contra o que a
   medição do piso sugere.
3. **Autorizar a Fase 3**: uma réplica no `ICMEZ_2025` (mesmo rig, 8 curvas já
   publicadas, basta repetir **uma** condição sem mudar o grip). Destrava 5
   curvas, das quais 4 já passam MAE e res.máx.

⇒ minha recomendação: **(1) + (3)**. Parar de gastar forma onde a rota está
fechada, e gastar **dado** onde a régua não é julgável.

## 6. Reprodutibilidade

```bash
py -3.12 New_Theory/lista_abertas.py
py -3.12 New_Theory/regra_de_parada_triagem.py
```
As distâncias e os pisos por fonte saem de `rh.limite_sres` / `rh.sres_para_censo`
e de `T.piso_da_fonte` — os mesmos helpers do report. Nada foi escrito.
