# Prereg — `surface_damage` D contra a classe "aceleração tardia" (o único amplificador)

**2026-08-01** · sequência do `crash_trigger` falsificado por construção.
O requisito ficou preciso: **fator > 1 sobre a taxa, governado por estado
acumulado**. No engine inteiro só um mecanismo tem isso.

## O candidato

`surface_damage` D cresce com a dissipação por slip acumulada
(`c_D`, `W_ref`) e **amplifica o wear**: `d_wear ·= (1 + k_dmg_wear·D)`
— fator **> 1**, exatamente o contradomínio que falta. Também reduz
`mu_bearing` (`k_dmg_mu`), o que acelera o afrouxamento por outra via.
Default inerte (`c_D = k_dmg_mu = k_dmg_wear = 0`).

## ⚠️ O que já foi falsificado sobre ele (e por que este teste é outro)

`chu_veredicto_completo.md` (2026-07-28/29): grade de 54 pontos no CHU —
a máquina **produz o regime** (test2 fim 0,16 vs 0,14 medido) mas
**nenhuma dose única serve a fonte**, porque o relógio do dano é monótono
na amplitude e o padrão do CHU não é.

**Este prereg pergunta outra coisa**: não "uma dose salva o CHU", e sim
**"a classe de 7 fontes responde ao amplificador?"**. Se responder em
≥2 fontes independentes, é classe; se só o CHU voltar a falhar, o
veredicto de lá permanece e este morre com ele.

## Universo (declarado ANTES)

Mesmas fontes do prereg anterior — razão de inclinação terminal > 2,
excluídas as com cauda de fratura (LU_2024, YANG_2021): **YANG_2019 (4),
CHU_2026 (6), LIU_2025 (4), JCSR_2023 (2), SUN (1)**.

⚠️ **LIU_2025 e LIU_2022 já usam `c_D` adotado** (0,5/0,03) — nessas o
teste é *aumentar* o que existe, não ligar do zero; declarar o valor de
partida por fonte antes de mexer.

## Gates (imutáveis)

- **G0 (direção, 2 pontos)**: `c_D` ∈ {0,5; 2,0} com
  `k_dmg_wear=4, W_ref=1e4` (starters físicos do repo) tem de **baixar o
  fim** da curva em ≥3 das 5 fontes. Δ=0 exato ⇒ **conferir companheiros
  antes de declarar inerte** (lição do canal de flanco: o wear precisa
  estar VIVO na fonte, senão amplificar zero dá zero).
- **G1 (classe)**: com **um** valor por fonte, a soma dos MAE da fonte
  cai ≥15 % em **≥2 fontes independentes**.
- **G2 (nenhum caso pior)**: nenhuma curva piora >+0,01 em qualquer perna.
- **G3 (procedência)**: `c_D` lido do dado (ciclo onde a inclinação
  dobra), não varrido às cegas; `k_dmg_wear`/`W_ref` nos starters do repo.
- **INCONCLUSIVO**: se o amplificador exigir valor diferente por curva
  DENTRO da fonte, repete-se o veredicto do CHU — documentar e parar.

## Previsão registrada

Onde o wear carrega pouco da perda, amplificá-lo não move nada
(decomposição decide para alavanca multiplicativa — regra do repo). Já
medido hoje: no ROUSSEAU aço o wear é **1 %** e no LIU_2022 é 42–49 %.
Espera-se, então, **efeito nulo** em fontes wear-pobres e efeito real
onde o canal existe — e isso é o próprio teste da hipótese.
