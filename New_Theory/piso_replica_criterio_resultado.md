# O piso de réplica como árbitro: aplicado às 31 sem estatuto, **fecha a rota F7**

**2026-08-07** · só-leitura · **nada adotado** · corolário de
`arrest_exp_resultado.md`.

## Por que esta passada

O adendo do `arrest_exp_resultado.md` instalou um critério que a campanha não
tinha explícito: **candidato tem de ser medido contra o piso de réplica da
fonte**, não só contra o tripé — porque o BAUER mostrou uma família inteira
"fechando curvas" sem que nada tivesse sido medido.

O critério recém-instalado se aplica também **ao que já está aberto**. Rodei-o
nas **31 sem estatuto** do `mapa_das_65_fora.json`.

## O resultado: 30 das 31 são **singletons**

| situação | curvas |
|---|---:|
| grupo de 1 (nenhuma réplica na mesma condição) | **30** |
| grupo com réplicas genuínas | **1** |

Isso **confirma com varredura** o que a campanha já registrava por contagem
(*"27 não prováveis hoje — a fonte não tem réplica em condição repetida"*). Não
é lacuna de método: é lacuna de **dado**, e nenhuma decisão a resolve.

## A única com réplicas — e ela **falha**, do jeito que valida a regra

`yang2021_amp0p6mm_ax8kN_r1` tem duas réplicas genuínas (`r2`, `r3`) da mesma
condição (0,6 mm, 8 kN). Ela passa a barra FORTE **pelo MAE** — e é exatamente
por isso que ela é o teste do método:

| perna | piso | FORTE (`piso/√2`) | `r1` | veredito |
|---|---:|---:|---:|---|
| MAE | 0,0344 | 0,0243 | 0,0264 | (não viola o tripé) |
| **res.máx** | 0,0539 | 0,0381 | **0,1012** | ❌ **DESCOBERTA** |
| **σ_res** | 0,0109 | 0,0077 | **0,0317** | ❌ **DESCOBERTA** |

**F7 INVÁLIDA.** As duas pernas que a reprovam ficam descobertas — a `r1` erra
**1,9×** o piso no res.máx e **2,9×** no σ. Parar no MAE teria produzido uma
assinatura errada; é a mesma armadilha que gerou
`_EXCECOES_RETRATADAS_F7_PERNA_DESCOBERTA`.

## O que isto estabelece — e por que o resultado negativo é o valioso

**A rota F7 está fechada para a população aberta.** Não sobra curva sem estatuto
alcançável por prova de piso: 30 não têm com que provar, e a 1 que tem, falha.

E o par de medições do dia mostra que o piso **corta nos dois sentidos**, que é o
que o torna árbitro e não desculpa:

| família | piso de réplica | erro do modelo | leitura |
|---|---|---|---|
| **BAUER fig6** (6 réplicas) | MAE **0,1065** — enorme | 0,024–0,078 | modelo **abaixo** do ruído ⇒ "melhoria" não é medível |
| **YANG_2021 0,6 mm** (3 réplicas) | res.máx **0,0539** · σ **0,0109** — minúsculo | 0,1012 / 0,0317 | modelo **muito acima** ⇒ erro é real |

As réplicas do YANG_2021 concordam entre si cerca de **3×** melhor do que o
modelo concorda com a `r1`. Nenhum argumento de dispersão a socorre.

⚠️ **Nota de procedência sobre a `r1`:** ela saiu do tripé **por mérito** na
correção D-U (2026-08-06), quando as 6 digitalizações originais do YANG_2021
foram re-ancoradas pelos centros do vetor — *"estava dentro por artefato, custo
declarado ANTES"*. Esta passada confirma que a saída é legítima e que **não há
rota de estatuto** para ela: o defeito é do modelo, contra dado reprodutível.

## Reprodutibilidade

O agrupamento por condição sai do `mapa_das_65_fora.json` + `case_registry`; os
pisos, de `itertools.combinations` sobre os `metric_data` do store, interpolados
na janela comum (mesmo método do `rh._pisos_medidos`). Segundos.
