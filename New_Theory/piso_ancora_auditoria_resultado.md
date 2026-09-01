# Auditoria de ÂNCORA nos pisos de réplica: **2 famílias infladas de 24** — e as 2 exceções em jogo **sobrevivem**

**2026-08-10** · só-leitura + 1 bloqueio de higiene · store `bd74eaf0b11d`, censo **147/205** ·
consequência direta do achado de `yang2021_ancora_replicas_resultado.md`.

## A pergunta

Ontem medi que, no `YANG_2021`, o piso de réplica calculado no **cru** inflava até **4×** porque
as réplicas têm **janelas de digitalização diferentes** e o `align` canônico normaliza cada uma
no **seu próprio** primeiro ponto. A pergunta óbvia: **quantas outras famílias têm esse defeito,
e alguma exceção assinada se apoia num piso inflado?**

Esta auditoria só pode **custar** — se achar piso inflado sob exceção, a exceção cai. É por isso
que vale rodá-la.

## O resultado: 2 de ~24 famílias, as duas no `YANG_2021`

Varri **todas** as famílias de réplica (chave mecânica `(fonte, δ, F_amp, modo)`, ≥2 membros),
comparando o piso **cru** ao piso **re-ancorado na janela comum**:

| família | membros | 1ºs pontos | piso cru | re-ancorado | inflação |
|---|---:|---|---:|---:|---:|
| **`(YANG_2021, 0.6)`** | 3 | 18 … 500 | 0,0344 | **0,0187** | **1,84×** |
| **`(YANG_2021, 0.8)`** | 2 | 300 … 500 | 0,0308 | **0,0182** | **1,69×** |
| `(SUN_2025_CRIMP, 0.0)` | 2 | 102 … 255 | 0,0449 | 0,0902 | 0,50× *(deflaciona)* |
| todas as outras (~20) | — | idênticos | — | — | **1,00×** |

⇒ **o defeito é raro**: quase toda família tem os membros começando no **mesmo** ciclo, e aí
re-ancorar é identidade. Só o `YANG_2021` digitaliza a mesma condição de figuras que começam em
ciclos diferentes.

## ✅ E as 2 exceções em jogo NÃO caem — a prova gravada as absolve

A família `(YANG_2021, 0.8)` é composta por `yang2021_fig2_typical` e
`yang2021_amp0p8mm_ax6kN`, e **as duas carregam exceção assinada**. Antes de propor qualquer
retratação, li a prova:

| curva | prova F5 | prova F7 |
|---|---|---|
| `fig2_typical` | *"canal estrutural ξ-dependente confundido"* | **None** |
| `amp0p8mm_ax6kN` | *"canal estrutural ξ-dependente confundido"* | **None** |

⇒ a prova das duas é **§C, forma faltante** — **não** é prova de piso. O piso inflado **não
entra** no argumento delas. **Nada a retratar.**

E o piso também não afeta limite: `piso registrado YANG_2021 = None`, `limite_sres = 0,0250`
(o global vence). ⇒ **a inflação não tem consequência métrica em lugar nenhum hoje.**

⚠️ **Quinta vez nesta campanha que ler a prova gravada mudou a decisão.** Eu tinha uma auditoria
correta, um número real (1,69×) e duas exceções no alvo — e o que impediu a retratação foi
**abrir o registro** em vez de inferir do padrão.

## ⚠️ O que a auditoria de fato encontrou: um pareamento sobre condição ASSUMIDA

A `fig2_typical` é pareada com a `amp0p8` como réplica de δ = 0,8 mm. Mas a nota de aparato
registra:

> *"Fig. 2 é uma medição **INDEPENDENTE** da Fig. 6(a3) … sua condição permanece **não
> rotulada** no paper (0.8 mm é uma **suposição plausível** pela família de vidas)."*

⇒ a chave mecânica pareia uma condição **assumida** com uma **medida**. É a mesma classe dos
blocos já assinados: `ROUSSEAU` (espessuras diferentes pareadas) e `KARLSEN` (sistema de porca
diferente).

**Bloqueado** em `_SEM_FAMILIA_MECANICA`, com o motivo e a prova no código. **Inócuo hoje** — e
listado assim mesmo, exatamente pela política que o próprio arquivo declara: *"'inócuo hoje' não
é 'correto'"*. O efeito prático é impedir que uma **futura** prova F7 se apoie num par cujo piso
está 1,7× inflado por âncora.

Invariantes: `test_pares_piso_familia` + `test_medicoes_cruzadas` + `test_meta_numeros` —
**36/36**, censo **inalterado em 147** (como esperado: o piso já era `None`).

## O achado reutilizável, agora com escopo medido

A regra de ontem (*"piso cru mistura scatter físico com diferença de âncora"*) é **verdadeira e
rara**: **2 de 24 famílias**. O teste de triagem é barato — comparar os primeiros ciclos dos
membros — e deve preceder qualquer prova F7 nova:

1. se os membros começam no **mesmo** ciclo, o piso cru é o piso honesto;
2. se começam em ciclos **diferentes**, medir o piso **re-ancorado na janela comum** e usar o
   menor dos dois como barra;
3. se a diferença de janela vier de **condição não rotulada**, o par não é família — bloquear.

⚠️ Caso invertido também existe e vale registrar: `(SUN_2025_CRIMP, 0.0)` **deflaciona** (0,0449
→ 0,0902, 0,50×) — re-ancorar lá *aumenta* o piso. Ou seja a correção não tem sinal fixo, e usar
"o menor dos dois" é a escolha conservadora, não a automática.

## Reprodutibilidade

`piso_ancora_audit.py` no scratchpad: varre as famílias do store, interpola na janela comum e
compara `MAE(cru)` com `MAE(re-ancorado)`. Segundos, só-leitura.
