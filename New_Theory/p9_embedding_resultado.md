# P-9 fica **cirúrgica**: falta frequência no `EmbeddingLoss`, não "nos relógios de Estágio I"

**2026-08-07** · só-leitura · **nada implementado** · afia a P-9 sem mudar o
veredito dela.

## O método, aplicado pela terceira vez no dia

Duas vezes hoje a pergunta *"o engine já tem essa forma?"* mudou o resultado: a
lei do platô da P-13 **existia** (`arrest_approach_exp`) e o `graded_scrit`
existia sem caso de uso. Apliquei a mesma pergunta à P-9 antes de tratá-la como
forma nova.

## A resposta: **metade** do Estágio I já tem o eixo

| mecanismo | lê `freq`? | evidência |
|---|---|---|
| **`CreepLoss`** | **sim** | 4 sítios; `t_cur = cycle_N / freq`, `t_prev = (cycle_N−1) / freq` — converte ciclo em **tempo** |
| **`EmbeddingLoss`** | **não** | `freq` aparece **só na assinatura** do `rate()`, nunca no corpo |

O creep é temporal por construção (`δ = C·log(t/t₀+1)`), logo a mesma contagem de
ciclos a 5 Hz e a 10 Hz dá tempos diferentes ⇒ perdas diferentes. O embedding é
puramente **cíclico** (forma geométrica de estado): 1000 ciclos são 1000 ciclos,
a qualquer frequência.

## Isso podia ter derrubado a P-9 — e **não derruba**

O critério que definiu a P-9 (`espelhado_classe_assinatura.py`) exigia
*"≥ 80 % da perda vindo de **emb + creep**"* — a **soma**. Se as curvas dela
fossem dominadas por creep, o eixo já existiria e o defeito estaria noutro
lugar. Separei:

| curva | emb % | creep % | dominante |
|---|---:|---:|---|
| `lu2024_fig14_amp0p5_long` | **97,3** | 1,8 | EMB |
| `lu2024_fig20_T22Nm` | **96,0** | 1,2 | EMB |
| `eccles2010_fig6_4kN_axial` | **79,1** | 5,7 | EMB |
| `yang2019_amp0p6_10Hz` | **79,8** | 20,2 | EMB |
| `yang2019_amp0p4_5Hz` | **75,1** | 24,9 | EMB |
| `liu2025_M16_amp0p3` | **63,8** | 36,2 | EMB |

**Unânime: 12 de 12 dominadas por embedding**, entre **64 % e 97 %**, em
**quatro fontes independentes** (ECCLES · LIU_2025 · LU_2024 · YANG_2019). O
mecanismo que carrega a perda é exatamente o que **não** lê frequência.

## O que muda no pedido

**Antes:** *"falta o eixo de frequência nos relógios de Estágio I"* — plural,
difuso, sem alvo de código.

**Agora:**

> falta o eixo de frequência no **`EmbeddingLoss`**. O `CreepLoss` já o tem e
> carrega 0,3–36 % nestas curvas; o embedding carrega 64–97 % e é puramente
> cíclico.

E vem com **molde**: o `CreepLoss` mostra como o engine expressa relógio
**temporal** em vez de cíclico (`t = N/freq`, incremento entre `t_prev` e
`t_cur`). Um embedding com componente dependente do tempo seguiria o mesmo
padrão, com o mesmo cuidado de estado incremental que a versão state-based já
tem.

⚠️ **O que isto NÃO estabelece.** Que a lei correta seja `1/f`, nem que o
embedding *deva* ser temporal — assentamento plástico é plausivelmente cíclico
mesmo. O que está medido é que **o canal que carrega a perda não tem o eixo que
o dado exige**, e que o outro canal, que tem o eixo, é pequeno demais para
suprir. A escolha da lei é decisão sua e exige prereg.

⚠️ **A autoridade medida antes segue valendo** (97–100 %): a `s1_amp_gate` já
gateia embedding **e** creep por amplitude e é default-inerte — logo existe
precedente estrutural de gate sobre o `d_delta` do Estágio I. Um gate de
frequência entraria no mesmo ponto.

## Reprodutibilidade

A varredura de menções a `freq` é leitura direta das classes
`EmbeddingLoss`/`CreepLoss` em `dynamic_stiffness_analyzer.py`; o split emb/creep
sai do `decomp` do store no ponto em que 10 % da pré-carga foi perdida (mesmo
ponto que `espelhado_classe_assinatura.py` usa). Segundos.
