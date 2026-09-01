# Prereg — relógio por reaperto, COMPOSIÇÃO corrigida (o operador atravessa o 1)

**2026-08-05** · decisão D-K (por delegação, MANDATO PERMANENTE) · gates
escritos **antes** de medir. Fingerprint de partida: `98fd6c462968`.

## O que o D-J falsificou, e por que isto não é reciclagem

O D-J testou `(1 + gain)^n` sobre o canal de slip, deixando a **queda** em n=1
para o `k_emb_renew`. **FALSIFICADO** — 0 de 20 células melhoraram as duas
cadeias, e a razão é algébrica, não empírica:

| estágio | fator NECESSÁRIO | base | melhor célula D-J |
|---|---:|---:|---:|
| t1 | **0,203** | 0,203 | 0,221 |
| t2 | 0,355 | 0,355 | **0,306** |
| t3 | 0,719 | 0,719 | **0,460** |

O fator necessário é **< 1 em todos os estágios reapertados** e **cresce para
1**. Um multiplicador de contradomínio **[1, ∞)** cresce na direção certa mas
**começa acima de 1**; e o `k_emb_renew` não tem autoridade para a queda —
alcança só o embedding (~45 % da perda), não os 5× pedidos.

**É a imagem espelhada da falsificação de 2026-08-02**: lá a família de gates
tinha contradomínio (0,1] e por isso *só sabia atrasar*; aqui o amplificador
tem [1, ∞) e *só sabe amplificar*. O dado pede um operador que **atravesse o
1**. Isto é composição errada, não relógio errado — e o mandato manda reabrir
quando o instrumento muda.

## A forma, e o número que ela pré-registra

```
fator(n) = 1                            se n = 0   (virgem, intocado)
fator(n) = retight_loss_base            se n = 1
         · (1 + retight_loss_gain)^(n-1) se n > 1
```

`retight_loss_base = 1.0` = OFF exato (junto com `gain = 0`), mantendo os dois
modos de inércia do D-J.

Ajuste fechado dos fatores medidos, **antes** de simular:

| cadeia | f₁ | g | previsto | necessário |
|---|---:|---:|---|---|
| fig8 (seco) | 0,203 | **1,88** | 0,203 · 0,382 · 0,718 | 0,203 · 0,355 · 0,719 |
| fig7a (óleo) | 0,483 | **1,74** | 0,483 · 0,840 · 1,462 | 0,483 · 0,720 · 1,464 |

⇒ **g difere 8 % entre as lubrificações; f₁ difere 2,4×.** É isso que sustenta
a divisão: **g COMPARTILHADO** (mecanismo — a taxa de re-dano por evento é da
superfície, não do lubrificante) e **f₁ POR GRUPO** (como `c_D` e `mu` já são).

## Gates (IMUTÁVEIS a partir daqui)

- **G0 (inércia exata):** `retight_loss_base=1,0` **e** `gain=0` ⇒ as 21 curvas
  com cadeia ficam **bit-idênticas**; e `n=0` ⇒ fator 1,0 para quaisquer
  valores.
- **G1 (MECANISMO — o gate que decide):** **um único `g`**, compartilhado por
  seco e óleo, com `f₁` por grupo. As **duas** cadeias têm de melhorar (soma de
  MAE cai em cada uma). Se só um `g` por lubrificação funcionar, o ramo é
  **FALSIFICADO** — o valor deste candidato está inteiro na transferência, e
  isso está escrito antes de medir.
- **G2 (virgem intocado):** `fig8_t0`, `fig7a_t0` e as 4 do `fig5`
  **bit-idênticas**.
- **G3 (protocolo que SOLTA):** as 8 do `fig6a`/`fig6b` **bit-idênticas**.
- **G4 (nenhum caso pior):** nenhuma das 9 piora > **+0,010** em qualquer
  perna; as 4 do `fig7a` e a `fig8_t3`, hoje no tripé, **permanecem**. A
  `fig8_t3` é o ponto de tensão real (n=3, onde o fator é maior).
- **G5 (ganho):** ≥ **2** das 3 de fila entram. Uma só ⇒ parcial declarada.
- **G6 (procedência):** `g` é **fit de 1 número sobre 2 cadeias**; `f₁` é fit
  de 1 número por grupo. Total **3 números para 9 curvas**. Se o `g` adotado
  ficar fora de **1,6–2,1**, declarar — a aritmética prevê 1,74–1,88.
- **G7 (sincronia + higiene do campo novo):** `VarSpec` no explorador para os
  **dois** campos novos (senão `test_all_fields_covered` falha), entrada em
  `_sem_dof_fitado` se não adotado, teto de DOF revisto com motivo, e teste de
  invariante dedicado.

### Ramos

- **ADOTA** — G0..G5.
- **FALSIFICADO (não transfere)** — precisa de `g` diferente por lubrificação.
- **FALSIFICADO (canal errado)** — nem com a composição correta o canal de
  slip produz os fatores; a forma faltante não está nele. ⇒ **a classe fecha**,
  com o membro finalmente testado por discriminante válido.
- **NÃO ADOTA (controle paga)** — G2/G3/G4 reprovam.
- **INCONCLUSIVO** — campo inerte por companheiro, ou fator não chega ao canal.

## Previsão registrada

Espero `g ≈ 1,8` **único**, `f₁ ≈ 0,20` (fig8) e `≈ 0,48` (fig7a); **t1 e t2
fechando** e a **t4 não** (fratura, canal de fadiga desligado no grupo).
Espero a `fig8_t3` **sob tensão** — é ela que o D-J destruiu (+0,127) e é o
G4 nela que decide se a composição corrigida basta.

⚠️ **Risco declarado de sobreajuste:** 3 números para 9 curvas, com 2 deles
per-grupo. O que separa isto de fudge é **exclusivamente** o G1 — se `g` não
for único, eu prefiro o ramo FALSIFICADO a soltar o segundo `g`.
