# O critério (c) da regra de parada ficou **indefinível** — a fila mudou de espécie

**2026-08-14** · só-leitura · **nada adotado** · store `cb019d75c6c2`, censo **140/205** ·
módulos limpos no HEAD `9653889`.

## A pendência que fui resolver

`New_Theory/regra_de_parada_proposta.md` aguarda assinatura, e o próprio registro marca um
número por re-derivar: o critério **(c)** — *"retorno marginal nulo: os 3 últimos candidatos
dão zero saídas por mérito **e** a mediana da distância cai menos de **3 %** relativos"* —
com a nota de que *"o 3 % foi derivado da fila e **precisa ser re-derivado**"* (era 1/3 da
mediana de 9 % sob a régua global; sob a régua por fonte a mediana era 13 %).

Re-derivar isso é **medição**, não assinatura. Fui fazer.

## O número saiu, e é inútil

| | quando a regra foi escrita | **hoje** |
|---|---:|---:|
| mediana da redução de σ necessária | **13 %** | **69 %** |
| curvas a ≤ 20 % do limite | várias | **0** |
| fontes representadas na fila | 9 | **1** |
| tamanho da fila | 26 | **8** |

Pela regra de bolso (`mediana/3`), o novo limiar seria **23 %**. **Não publico esse número
como re-derivação**, e o motivo não é aritmético.

## ⚠️ Por que o critério ficou indefinível

O (c) mede **retorno marginal do esforço** sobre a classe form-limited: *"gastamos três
candidatos e a fila mal se moveu, logo pare"*. Ele pressupõe uma fila em que **trabalho é
possível** — foi assim que foi desenhado, sobre 26 curvas de 9 fontes.

Hoje a fila é **8 curvas, todas do `LU_2024`, todas órfãs de protocolo** (item **F** da mesa),
e **três instrumentos independentes** já mostraram que **não há rota**: (a) grade
pré-registrada com o censo do LU **plano** em toda a região de alavancas; (b) o paper separa
§3.1.3 (half-sine de máquina) do §3.2 (manual), logo não há réplica no mesmo protocolo para
dar piso; (c) fonte fechada, sem dado novo. E a quarta rota — modelar a forma de onda — **eu
falsifiquei** hoje (`lu2024_halfsine_forma_onda_falsificada.md`).

⇒ **o critério (c) dispararia HOJE, e dispararia pelo motivo errado.** Ele concluiria "retorno
marginal nulo" não porque o esforço se esgotou, mas porque **a fila inteira está bloqueada por
dado**. São coisas diferentes:

| o (c) foi desenhado para detectar | o que ele detectaria hoje |
|---|---|
| esgotamento de **ideias** sobre uma classe de defeito trabalhável | ausência de **dado** numa fonte específica |

Assinar a regra agora deixaria "parar" ser concluído por uma condição que ela não testa.

## O que proponho (e o que não)

**Não** proponho mudar o critério — a regra é do professor e alterá-la exige assinatura.

**Proponho registrar** que o (c) **não é avaliável** enquanto a fila for monofonte e
data-blocked, e que a re-derivação pedida **não deve ser feita com estes 69 %**: um limiar
tirado de uma fila de 8 curvas de uma fonte sem rota não descreve retorno marginal de nada.

Duas saídas honestas, ambas de assinatura:

1. **decidir o item F primeiro** (declarar as 8 como classe "órfã de protocolo") — a fila
   esvazia, o (c) fica sem população e a regra de parada passa a ser sobre **outra** coisa;
2. **manter o (c) suspenso** até a fila voltar a ter ≥2 fontes com rota, e re-derivar o
   limiar então, sobre a população para a qual ele foi desenhado.

⚠️ Registro o incentivo contrário, como em todas as propostas deste dia: a saída fácil é
re-derivar 23 % e seguir — o número existe, é defensável aritmeticamente, e ninguém notaria.
Ele só não mede o que o critério diz medir.

## Reprodutibilidade

`regra_de_parada_triagem.py` (bloco "redução de σ_res necessária"); comparação com os valores
citados em `regra_de_parada_proposta.md`. Segundos, só-leitura.
