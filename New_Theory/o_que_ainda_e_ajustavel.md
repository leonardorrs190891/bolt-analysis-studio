# O que ainda é ajustável nas curvas — diagnóstico de CLASSE (não de caso)

**2026-08-01** · resposta medida à pergunta do professor. Store
`a410d6537c83`, censo 132/205, fila sem estatuto = 32 curvas.

## O teste que separa "ajustável" de "não ajustável"

Uma **constante** (per-rig) move o **nível** do grupo inteiro na mesma
direção. Logo ela só pode resolver um grupo se o **viés
(modelo − dado) tiver SINAL ÚNICO** nas curvas daquele grupo. Se os
sinais são opostos, qualquer constante melhora umas e piora outras —
matematicamente, não por azar.

Aplicado a todas as fontes com curva na fila:

| classe | fontes | leitura |
|---|---|---|
| **A — viés de sinal único** (constante ainda pode agir) | **CACCESE_2009** (1 de 7 fora; viés −0,051 a −0,003) | única candidata legítima a ajuste de constante |
| **B — sinais opostos** (constante NÃO resolve) | CHU ·  ROUSSEAU · LIU_2025 · YANG_2019 · LIU_2022_RETIGHT · LI_2022_TRIBOINT · LU_2024 · YANG_2021 · SUN · IJPEM | 31 das 32 curvas da fila |

## Conclusão: o poço das constantes secou

**31 das 32 curvas que faltam estão em fontes onde o viés troca de sinal
dentro do próprio grupo.** Não é falta de calibração — é o modelo não
reproduzir uma **tendência** dentro da família:

- **ROUSSEAU** (spread 0,138): tendência com **espessura** — t10/t12
  retêm demais (+0,051/+0,057), t14 de menos (−0,043).
- **LI_2022_TRIBOINT** (0,068): tendência com **frequência** — +0,053 a
  10 Hz, +0,027 a 15 Hz, −0,016 a 20 Hz, monotônica.
- **LIU_2022_RETIGHT** (0,095): tendência com **índice de reaperto**
  (medido hoje no prereg do flanco: o canal ajuda t4 e atrapalha t1/t2).
- **CHU** (0,193) e **YANG_2019** (0,114): tendência com amplitude/
  espectro, já varridas e falsificadas.

Verificações feitas hoje que sustentam isso (não é inferência):
`C_creep` ×2 na família de frequência → viés vai de +0,05 a **−0,10**
(sensível demais, e na direção errada); `fret_freq_exp` **não toca** a
curva de 10 Hz por construção (o fator vale 1 em `f=f_ref`); no Rousseau
o `loose_arrest_floor` já foi lido do aparato e o que restou é o
degrau de espessura.

## O que isso implica para o esforço

1. **Parar de procurar constantes** nas fontes da classe B — a
   medição diz que não existem. Cada tentativa vai redistribuir erro (foi
   o que os 3 preregs de hoje mostraram: amplitude, flanco, creep).
2. **A única constante ainda viva** é a do CACCESE_2009 (1 curva,
   sinal único) — e a fonte tem 7 curvas, então a barra do "nenhum caso
   pior" é dura.
3. **O que resta é FORMA** — e a regra do dia vale: só abrir forma nova
   com dado que a exija **em mais de uma fonte**. Hoje há três tendências
   nomeadas (espessura, frequência, índice de reaperto) e nenhuma delas
   apareceu em duas fontes independentes ainda.
4. **A rota mais barata não é modelar, é LER**: o Rousseau rendeu 1 tripé
   e 1 constante de aparato só relendo o PDF. Fontes com PDF na
   biblioteca e constantes ainda marcadas "fitado-this-rig":
   YANG_2019/YANG_2021/IJPEM (`c_bend`, `k_ratchet`), LIU_2025 e
   LIU_2022_RETIGHT (`C_creep`, `loose_arrest_floor`), LI_2022_TRIBOINT
   (6 constantes).

**Resposta curta à pergunta**: dá para continuar ajustando **uma** curva
por constante (CACCESE) e um punhado por leitura de aparato; as outras 31
pedem forma — e a forma só se justifica quando a mesma tendência
aparecer em duas fontes independentes.
