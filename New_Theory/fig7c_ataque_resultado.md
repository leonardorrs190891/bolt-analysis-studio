# `eccles2010_fig7c` atacada — fecha com **um** número, e esse número é proibido

**2026-08-09** · só-leitura · **nada adotado** · pedido direto do professor
(*"ataque eccles2010_fig7c_axial_2p7kN_constant"*).

## O alvo

A curva que saiu do tripé na **P-15** ao perder o piso falso da fonte. Estado:

| perna | valor | limite | múltiplo |
|---|---:|---:|---:|
| MAE | 0,0250 | 0,050 | **0,50×** |
| res.máx | 0,0612 | 0,100 | **0,61×** |
| **σ_res** | **0,0258** | 0,0250 | **1,03×** ← única violada |

**Duas pernas passam com folga de 2×; a terceira falha por 3 %.** É a curva mais
próxima do tripé em toda a fila.

## O defeito tem forma nomeada: **curvatura**

| terço do ensaio | resíduo médio |
|---|---:|
| 1º | **+0,0104** |
| 2º | −0,0217 |
| 3º | −0,0223 |

**Troca de sinal**, com **35 %** da variância **entre** terços. O modelo perde
devagar demais no começo e demais no fim — não é erro de nível, é de **forma**.
É a classe que o `sigma_res_decomposicao_por_estagio.md` (2026-07-29) já
identificara como a que **alavanca de escala não move**.

Decomposição: **rotacional 64 % · embedding 32 %** · wear 2 % · creep 2 %.

Detalhe revelador: `loose_arrest_floor` = **0,182**, mas o modelo termina em
**0,1655** — ele **passa do piso**, porque o rotacional arresta e o **embedding
continua descendo** depois.

## O que foi testado — e por que cada rota fecha

| alavanca | resultado | por que não serve |
|---|---|---|
| `arrest_approach_exp` 1,5 / 2 / 3 | σ **0,0416 / 0,0566 / 0,0790** | **direção errada**, e piora forte |
| `loose_arrest_floor` 0,19 / 0,20 / 0,21 | σ 0,0254 / **0,0251** / 0,0254 | **procedência travada** (ver abaixo) |
| `emb_slip_gate` 0,5 / 0,8 | **idêntico** ao nominal | inerte nesta curva |
| `k_wear_spec` 1e-15 / 6e-15 | σ 0,0255 / 0,0268 | insuficiente |
| **`N_emb` 30 / 35 / 40** | **fecha as 3 pernas** | **sem procedência, e o dado aponta ao contrário** |

## ⛔ As duas rotas que fechariam, e por que estão bloqueadas

### 1. O piso — travado por procedência, e ela foi **verificada**

`loose_arrest_floor` a 0,20 dá σ **0,0251** (1,004× — 0,4 % do limite) e ainda
melhora o MAE em 40 %. Mas o `prov` diz:

> *"**lido-do-dado** (assíntota final crua ≥0,03; física = torque de prevalência)"*

Conferido contra a CSV crua: o final é **0,1800** e a constante é **0,182** —
**bate** dentro da tolerância. A constante **obedece à própria regra**. Movê-la
para 0,20 seria trocar procedência por placar.

### 2. O `N_emb` — fecha, mas o dado aponta para o **lado oposto**

`N_emb` = 40 fecha as três pernas (0,0229 / 0,0618 / **0,0209**). Mas `N_emb` = 50
é o **default do engine** (o config do ECCLES não o sobrescreve), então 40 seria
**número novo**. Existe rota de procedência? Não há leitor de `N_emb` em
`provenance.py` (só `emb_depth_from_curve` e `arrest_floor_from_curve`), então
**li do transiente**: o ciclo em que a queda atinge 63,2 % do total.

| | `N_emb` |
|---|---:|
| default do engine | 50 |
| **lido do dado (fig7c)** | **≈ 93,5** |
| lido nas outras 8 do ECCLES | **84 – 116** |
| **que fecha o tripé** | **40** |

⇒ **o dado pede N maior; a métrica pede menor.** Adotar 40 seria fitar à métrica
**contra a evidência do próprio dado**. Bloqueado.

⚠️ **Ressalva honesta:** essa leitura mede a constante de tempo **composta**
(embedding é só 32 % da perda), então 93,5 não é leitura limpa do embedding. Mas
a **direção** é inequívoca, e é ela que decide.

## Conclusão: form-limited de verdade, e a 3 %

A `fig7c` **não é fechável por constante**. Todas as alavancas disponíveis ou
têm procedência travada, ou apontam na direção errada, ou fecham a métrica
contra o dado. O defeito é **curvatura** — a classe que a campanha já
estabeleceu como exigindo **forma**, não constante.

⚠️ **É a candidata mais forte da fila para uma forma de curvatura:** só uma perna
viola, por 3 %, com as outras duas em 0,5–0,6× do limite. Qualquer forma que
corrija a curvatura sem estragar nível a fecha.

⚠️ **E ela não tem rota F7:** o `ECCLES_2010` perdeu o piso medido na P-15 (a
família era a variável varrida), então prova de piso é impossível até haver
réplica de condição repetida.

## Reprodutibilidade

Sondas no scratchpad: 2 pontos por alavanca + grade, leitura do `N_emb` do
transiente e conferência do `loose_arrest_floor` contra a CSV crua. Minutos.
