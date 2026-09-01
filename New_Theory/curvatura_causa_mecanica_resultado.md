# A causa do split de curvatura é **mecânica**, e nomeia um culpado por sub-classe

**2026-08-09** · só-leitura · **nada adotado** · continuação de
`curvatura_duas_classes_resultado.md`, que deixara a causa física **declarada
como não testada**.

## O teste

Para cada curva das duas sub-classes, a fatia de cada mecanismo no
**incremento** do 1º terço e do último — *qual mecanismo carrega a perda cedo,
qual carrega tarde*. Incremento, não acumulado: é o que governa a **forma**.

## O resultado: assinaturas opostas, e o discriminante é o **rotacional**

| | rotacional cedo → tarde | wear cedo → tarde | emb+creep cedo |
|---|---|---|---|
| **A** (10 curvas) | **0 % → 30 %** | 18 % → 37 % | **81 %** |
| **B** (5 curvas) | **37 % → 2 %** | **1 % → 57 %** | 62 % |

O canal rotacional **liga tarde** na A e **desliga** na B — perfeitamente
invertido. Isso eleva o split de **fenomenológico** (forma do resíduo) a
**mecânico** (qual canal age quando).

## A leitura de cada lado

### A — os relógios de Estágio I são rápidos demais

O resíduo é negativo cedo (modelo **abaixo** do dado ⇒ perdeu **mais**) enquanto
**embedding + creep carregam 81 %** e o rotacional carrega **zero**. Depois o
resíduo vira positivo: o rotacional chega (30 %) mas **tarde demais** para
sustentar a queda que o dado tem no fim.

⇒ **culpado: o relógio de Estágio I dispara cedo demais.**

⚠️ **Isto é a família da P-9** — e a confirmação é forte: a
`yang2019_amp0p6_10Hz`, que a P-9 acabou de melhorar em 81 % de viés, **está na
sub-classe A**, e 4 das 10 são do `YANG_2019`. A P-9 atacou o mecanismo certo;
só não alcançou as outras porque **as fontes restantes são mono-frequência**.

### B — o wear sobra depois que o rotacional arresta

O resíduo é positivo cedo (modelo **acima** ⇒ perdeu **menos**) com o rotacional
já em 37 %. No fim ele arresta (2 %) e o **wear assume 57 %** — e é aí que o
modelo **passa** do dado (resíduo negativo).

⇒ **culpado: o wear continua em taxa plena depois que o afrouxamento parou.**

Isso bate com o que a sonda da `fig7c` já mostrara por outro caminho: o
`loose_arrest_floor` para o rotacional em 0,182 mas **o modelo termina em
0,1655** — passa do piso porque outro canal continua. E baixar `k_wear_spec`
melhorava o σ (0,0258 → 0,0255) enquanto subir piorava (0,0268): direção
coerente, magnitude insuficiente sozinha.

## O que isto propõe (não executado)

Para a **B**, uma forma com nome preciso: **o wear deveria desacelerar quando o
slip para**. Hoje o `WearLoss` é Archard sobre o slip resolvido; se o
afrouxamento arresta mas o slip transversal continua, o wear segue em taxa
plena. Fisicamente, superfície já conformada remove menos material por ciclo —
e o engine tem `k_wear_running` (running-in), que é o **inverso** disto (taxa
maior no início), sem o irmão de saturação.

Para a **A**, a rota já está aberta e parcialmente executada: é a P-9, limitada
por **identificabilidade** (só o `YANG_2019` varre frequência).

## ⚠️ O que NÃO está estabelecido

Que a assinatura seja **causa** e não **consequência**. As fatias são atribuição
*a posteriori* de uma parametrização — o `CLAUDE.md` já registra que decomposição
não decide quando a alavanca **substitui a lei**. O que está medido é que os dois
grupos têm **sequências de mecanismo opostas**, o que é forte o bastante para
**dirigir** o próximo candidato, não para adotá-lo.

## Reprodutibilidade

Sonda no scratchpad: fatia de cada mecanismo no incremento do 1º e do último
terço, agrupada pelo sinal de `r(3/3) − r(1/3)`. Segundos.
